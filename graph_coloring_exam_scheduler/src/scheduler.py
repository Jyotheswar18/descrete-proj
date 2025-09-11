import pandas as pd
import networkx as nx

def build_graph(students_file):
    # Load student-course mapping
    df = pd.read_csv(students_file)

    # Get unique subjects (exam_subject)
    subjects = df['exam_subject'].unique()
    graph = nx.Graph()

    # Add subjects as nodes
    graph.add_nodes_from(subjects)

    # Create edges where students share subjects
    student_groups = df.groupby('regno')['exam_subject'].apply(list)
    for courses_list in student_groups:
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
    timetable = pd.DataFrame(list(coloring.items()), columns=["exam_subject", "time_slot"])
    final = pd.merge(timetable, courses, left_on="exam_subject", right_on="course_code")
    final.sort_values(by="time_slot", inplace=True)
    final.to_csv(output_file, index=False)
    return final
