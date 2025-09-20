from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data')
OUTPUT_PATH = os.path.join(BASE_DIR, 'output')
STATIC_PATH = os.path.join(BASE_DIR, 'static')
TEMPLATES_PATH = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_PATH, static_folder=STATIC_PATH)

def get_stats():
    # Count students
    students_file = os.path.join(DATA_PATH, 'students.csv')
    courses_file = os.path.join(DATA_PATH, 'courses.csv')
    timetable_file = os.path.join(OUTPUT_PATH, 'timetable.csv')
    # Students
    try:
        with open(students_file, 'r', encoding='utf-8') as f:
            students = list(csv.reader(f))
            student_count = len(students) - 1 if students else 0
    except Exception:
        student_count = 0
    # Courses
    try:
        with open(courses_file, 'r', encoding='utf-8') as f:
            courses = list(csv.reader(f))
            course_count = len(courses) - 1 if courses else 0
    except Exception:
        course_count = 0
    # Slots
    try:
        with open(timetable_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            slots = [row['slot'] for row in reader if 'slot' in row]
            slot_count = len(set(slots))
    except Exception:
        slot_count = 0
    return {
        'students': student_count,
        'courses': course_count,
        'slots': slot_count
    }



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    filter_type = request.form.get('filter_type')
    filter_value = request.form.get('filter_value').strip()
    students = pd.read_csv(os.path.join(DATA_PATH, 'students.csv'))
    timetable = pd.read_csv(os.path.join(OUTPUT_PATH, 'timetable.csv'))
    courses = pd.read_csv(os.path.join(DATA_PATH, 'courses.csv'))

    import networkx as nx
    import matplotlib.pyplot as plt
    graph_image = None
    timetable_dict = None
    student_name = filter_value if filter_type == 'student' else None

    if filter_type == 'student':
        # Case sensitive search (no lower/upper conversion)
        student_row = students[students['student_name'].str.strip() == filter_value]
        if student_row.empty:
            return render_template('timetable.html', student_name=filter_value, timetable=None, graph_image=None)
        registered_courses = student_row.iloc[0]['registered_courses'].split('|')
        student_timetable = timetable[timetable['course_id'].isin(registered_courses)]
        merged = pd.merge(student_timetable, courses, on='course_id', how='left')
        timetable_list = []
        for _, row in merged.iterrows():
            timetable_list.append({
                'course_id': row['course_id'],
                'course_name': row['course_name'] if 'course_name' in row else row.get('subject', ''),
                'slot': row['time_slot'] if 'time_slot' in row else row.get('slot', '')
            })
        G = nx.Graph()
        for course in registered_courses:
            G.add_node(course)
        for i in range(len(registered_courses)):
            for j in range(i+1, len(registered_courses)):
                G.add_edge(registered_courses[i], registered_courses[j])
        graph_image = f"{filter_value}_graph.png"
        graph_path = os.path.join(STATIC_PATH, graph_image)
        plt.figure(figsize=(6,6))
        nx.draw(G, with_labels=True, node_color="skyblue", node_size=2000, font_size=12, font_color="black")
        plt.savefig(graph_path)
        plt.close()
        return render_template('timetable.html', student_name=filter_value, timetable=timetable_list, graph_image=graph_image)
    elif filter_type == 'course_id':
        course_id = filter_value
        course_row = courses[courses['course_id'] == course_id]
        if course_row.empty:
            return render_template('timetable.html', student_name=course_id, timetable=None, graph_image=None, table_type='course_id')
        # Find all students registered for this course
        student_rows = students[students['registered_courses'].apply(lambda x: course_id in x.split('|'))]
        timetable_list = []
        # Get course_name from courses.csv
        course_name = course_row.iloc[0]['course_name'] if 'course_name' in course_row.iloc[0] else ''
        for _, student_row in student_rows.iterrows():
            timetable_list.append({
                'student_id': student_row['student_id'],
                'student_name': student_row['student_name'],
                'course_name': course_name
            })
        # Graph: just this course as a node
        G = nx.Graph()
        G.add_node(course_id)
        graph_image = f"{course_id}_graph.png"
        graph_path = os.path.join(STATIC_PATH, graph_image)
        plt.figure(figsize=(4,4))
        nx.draw(G, with_labels=True, node_color="orange", node_size=2000, font_size=12, font_color="black")
        plt.savefig(graph_path)
        plt.close()
        return render_template('timetable.html', student_name=course_id, timetable=timetable_list, graph_image=graph_image, table_type='course_id')
    elif filter_type == 'slot':
        slot = filter_value
        slot_rows = timetable[timetable['time_slot'].astype(str) == str(slot)]
        # Courses in this slot
        courses_in_slot = []
        for _, row in slot_rows.iterrows():
            courses_in_slot.append({
                'course_id': row['course_id'],
                'course_name': row['course_name'] if 'course_name' in row else row.get('subject', '')
            })
        # Students writing exams in this slot
        students_in_slot = []
        for _, row in slot_rows.iterrows():
            course_id = row['course_id']
            student_rows = students[students['registered_courses'].apply(lambda x: course_id in x.split('|'))]
            for _, student_row in student_rows.iterrows():
                students_in_slot.append({
                    'student_id': student_row['student_id'],
                    'student_name': student_row['student_name'],
                    'course_id': course_id
                })
        # Graph: all courses in this slot
        import networkx as nx
        import matplotlib.pyplot as plt
        G = nx.Graph()
        for _, row in slot_rows.iterrows():
            G.add_node(row['course_id'])
        for i in range(len(slot_rows)):
            for j in range(i+1, len(slot_rows)):
                G.add_edge(slot_rows.iloc[i]['course_id'], slot_rows.iloc[j]['course_id'])
        graph_image = f"slot_{slot}_graph.png"
        graph_path = os.path.join(STATIC_PATH, graph_image)
        plt.figure(figsize=(6,6))
        nx.draw(G, with_labels=True, node_color="violet", node_size=2000, font_size=12, font_color="black")
        plt.savefig(graph_path)
        plt.close()
        return render_template('timetable.html', student_name=f"Slot {slot}", courses_in_slot=courses_in_slot, students_in_slot=students_in_slot, table_type='slot', graph_image=graph_image)
    elif filter_type == 'course_name':
        course_name = filter_value
        course_ids = courses[courses['subject'].str.lower() == course_name.lower()]['course_id'].tolist()
        if not course_ids:
            return render_template('timetable.html', student_name=course_name, timetable=None, graph_image=None)
        timetable_dict = {}
        for course_id in course_ids:
            # Find all students for this course
            student_rows = students[students['registered_courses'].apply(lambda x: course_id in x.split('|'))]
            for _, student_row in student_rows.iterrows():
                timetable_dict[student_row['student_name']] = course_id
        # Graph: all course_ids for this subject
        G = nx.Graph()
        for cid in course_ids:
            G.add_node(cid)
        for i in range(len(course_ids)):
            for j in range(i+1, len(course_ids)):
                G.add_edge(course_ids[i], course_ids[j])
        graph_image = f"{course_name}_graph.png"
        graph_path = os.path.join(STATIC_PATH, graph_image)
        plt.figure(figsize=(6,6))
        nx.draw(G, with_labels=True, node_color="lightgreen", node_size=2000, font_size=12, font_color="black")
        plt.savefig(graph_path)
        plt.close()
        return render_template('timetable.html', student_name=course_name, timetable=timetable_dict, graph_image=graph_image)
    else:
        return render_template('timetable.html', student_name=filter_value, timetable=None, graph_image=None)

if __name__ == '__main__':
    app.run(debug=True)
