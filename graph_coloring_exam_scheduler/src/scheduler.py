import pandas as pd
import networkx as nx

def build_graph(students_file):
    # Load student-course mapping
    df = pd.read_csv(students_file)

    # Get all unique course IDs from registered_courses
    all_courses = set()
    student_courses = []
    for courses_str in df['registered_courses']:
        courses = courses_str.split('|')
        student_courses.append(courses)
        all_courses.update(courses)

    graph = nx.Graph()
    graph.add_nodes_from(all_courses)

    # Create edges where students share courses
    for courses_list in student_courses:
        for i in range(len(courses_list)):
            for j in range(i + 1, len(courses_list)):
                graph.add_edge(courses_list[i], courses_list[j])

    return graph

def schedule_exams(graph):
    # Apply greedy coloring algorithm
    coloring = nx.coloring.greedy_color(graph, strategy="largest_first")
    return coloring

def save_timetable(coloring, courses_file, output_file):
    courses = pd.read_csv(courses_file)
    timetable = pd.DataFrame(list(coloring.items()), columns=["course_id", "time_slot"])
    final = pd.merge(timetable, courses, on="course_id")
    final.sort_values(by="time_slot", inplace=True)
    final.to_csv(output_file, index=False)
    return final
