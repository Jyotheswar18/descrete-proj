import matplotlib.pyplot as plt
import networkx as nx
from scheduler import build_graph, schedule_exams

# Fixed color map for 6 slots
SLOT_COLORS = {
    0: '#FFB300',  # Slot 1 - Yellow
    1: '#803E75',  # Slot 2 - Purple
    2: '#FF6800',  # Slot 3 - Orange
    3: '#A6BDD7',  # Slot 4 - Blue
    4: '#C10020',  # Slot 5 - Red
    5: '#CEA262',  # Slot 6 - Brown
}

def visualize_schedule(graph, coloring):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph, seed=42)
    # Map slot numbers to fixed colors
    node_colors = [SLOT_COLORS.get(coloring[node] % 6, '#CCCCCC') for node in graph.nodes()]
    labels = {node: f"{node}\nSlot {coloring[node] % 6 + 1}" for node in graph.nodes()}
    nodes = nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1200)
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, labels, font_size=12)
    plt.title("Exam Schedule Graph Coloring (6 Slots)", fontsize=16)
    # Color legend
    for slot, color in SLOT_COLORS.items():
        plt.scatter([], [], c=color, label=f"Slot {slot+1}")
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Time Slot Colors")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main():
    students_file = "../data/students.csv"
    graph = build_graph(students_file)
    coloring = schedule_exams(graph)
    visualize_schedule(graph, coloring)
    display_student_exams(students_file)
    display_timetable(students_file, coloring)
    # Example searches
    print("\n--- Search by Student (e.g. REG0001) ---")
    search_student_exams(students_file, 'REG0001')
    print("\n--- Search by Slot (e.g. Slot 1) ---")
    search_slot_exams(students_file, coloring, 

def display_timetable(students_file, coloring):
    import pandas as pd
    df = pd.read_csv(students_file)
    # Map each subject to its slot
    subject_slot = {subject: slot % 6 + 1 for subject, slot in coloring.items()}
    df['time_slot'] = df['exam_subject'].map(subject_slot)
    # Group by time_slot and exam_subject, count students
    summary = df.groupby(['time_slot', 'exam_subject']).agg(
        students=('regno', 'count'),
        student_list=('name', lambda x: ', '.join(x))
    ).reset_index()
    print("\n--- Timetable (Time Slot, Subject, No. of Students) ---\n")
    print(f"Total Time Slots: {summary['time_slot'].nunique()}")
    print(f"Total Subjects: {summary['exam_subject'].nunique()}")
    print(f"Total Students: {df['regno'].nunique()}")
    print("\n{:<8} {:<12} {:<8} {}".format('Slot', 'Subject', 'Count', 'Students'))
    print("-"*80)
    for _, row in summary.iterrows():
        print(f"{row['time_slot']:<8} {row['exam_subject']:<12} {row['students']:<8} {row['student_list']}")

def search_student_exams(students_file, regno):
    import pandas as pd
    df = pd.read_csv(students_file)
    exams = df[df['regno'] == regno]
    if exams.empty:
        print(f"No exams found for student {regno}.")
        return
    print(f"Exams for {regno} ({exams.iloc[0]['name']}):")
    for _, row in exams.iterrows():
        print(f"Subject: {row['exam_subject']}, Time: {row['exam_time']}, Slot: {row['slot']}")

def search_slot_exams(students_file, coloring, slot_num):
    import pandas as pd
    df = pd.read_csv(students_file)
    subject_slot = {subject: slot % 6 + 1 for subject, slot in coloring.items()}
    subjects_in_slot = [subj for subj, slot in subject_slot.items() if slot == slot_num]
    exams = df[df['exam_subject'].isin(subjects_in_slot)]
    if exams.empty:
        print(f"No exams found for Slot {slot_num}.")
        return
    print(f"Exams in Slot {slot_num}:")
    for _, row in exams.iterrows():
        print(f"Student: {row['name']} ({row['regno']}), Subject: {row['exam_subject']}, Time: {row['exam_time']}")

def display_student_exams(students_file):
    import pandas as pd
    df = pd.read_csv(students_file)
    print("\n--- Student Exam Details ---\n")
    for _, row in df.iterrows():
        print(f"RegNo: {row['regno']}, Name: {row['name']}, Subject: {row['exam_subject']}, Time: {row['exam_time']}, Slot: {row['slot']}")

if __name__ == "__main__":
    main()