from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os
from scheduler import build_graph, schedule_exams, save_timetable

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

SLOT_COLORS = {
    0: '#FFB300',  # Slot 1 - Yellow
    1: '#803E75',  # Slot 2 - Purple
    2: '#FF6800',  # Slot 3 - Orange
    3: '#A6BDD7',  # Slot 4 - Blue
    4: '#C10020',  # Slot 5 - Red
    5: '#CEA262',  # Slot 6 - Brown
}

STUDENTS_FILE = os.path.join(BASE_DIR, 'data', 'students.csv')
GRAPH_IMG = os.path.join(BASE_DIR, 'static', 'graph.png')

def get_dynamic_colors(n):
    cmap = cm.get_cmap('tab10' if n <= 10 else 'tab20')
    return [mcolors.rgb2hex(cmap(i / n)) for i in range(n)]

# Helper to get coloring and graph
def get_coloring_and_graph():
    graph = build_graph(STUDENTS_FILE)
    coloring = schedule_exams(graph)
    return graph, coloring

# Home page
@app.route('/')
def home():
    graph, coloring = get_coloring_and_graph()
    subjects = list(coloring.keys())
    slots = {subj: coloring[subj] % 6 + 1 for subj in subjects}
    save_graph_image(graph, coloring)
    # Generate timetable.csv
    save_timetable(coloring, os.path.join(BASE_DIR, 'data', 'courses.csv'), os.path.join(BASE_DIR, 'output', 'timetable.csv'))
    return render_template('index.html', subjects=subjects, slots=slots, slot_colors=SLOT_COLORS)

# Student search
@app.route('/student')
def student_search():
    regno = request.args.get('regno', '').strip()
    df = pd.read_csv(STUDENTS_FILE)
    exams = df[df['regno'] == regno]
    if exams.empty:
        return render_template('student.html', regno=regno, exams=None)
    subjects = exams['exam_subject'].tolist()
    graph, coloring = get_coloring_and_graph()
    save_graph_image(graph.subgraph(subjects), coloring, filename=os.path.join('..', 'static', 'student_graph.png'))
    return render_template('student.html', regno=regno, exams=exams, graph_img='../static/student_graph.png')

# Slot search
@app.route('/slot')
def slot_search():
    slot_num = int(request.args.get('slot', '1'))
    graph, coloring = get_coloring_and_graph()
    subject_slot = {subj: coloring[subj] + 1 for subj in coloring}
    subjects_in_slot = [subj for subj, slot in subject_slot.items() if slot == slot_num]
    df = pd.read_csv(STUDENTS_FILE)
    exams = df[df['exam_subject'].isin(subjects_in_slot)]
    save_graph_image(graph.subgraph(subjects_in_slot), coloring, filename=os.path.join('..', 'static', 'slot_graph.png'))
    return render_template('slot.html', slot_num=slot_num, exams=exams, subjects=subjects_in_slot, graph_img='../static/slot_graph.png', slot_colors=SLOT_COLORS)

# Subject search
@app.route('/subject')
def subject_search():
    subject = request.args.get('subject', '').strip()
    df = pd.read_csv(STUDENTS_FILE)
    exams = df[df['exam_subject'] == subject]
    graph, coloring = get_coloring_and_graph()
    save_graph_image(graph.subgraph([subject]), coloring, filename=os.path.join('..', 'static', 'subject_graph.png'))
    return render_template('subject.html', subject=subject, exams=exams, graph_img='../static/subject_graph.png', slot_colors=SLOT_COLORS)

# Timetable
@app.route('/timetable')
def timetable():
    # Read generated timetable.csv
    timetable_path = os.path.join(BASE_DIR, 'output', 'timetable.csv')
    timetable_df = pd.read_csv(timetable_path)
    # Display as neat HTML table
    return render_template('timetable.html', timetable=timetable_df, slot_colors=SLOT_COLORS)

# Helper to save graph image
def save_graph_image(graph, coloring, filename=GRAPH_IMG):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph, seed=42)
    node_colors = []
    n_colors = max(coloring.values()) + 1
    dynamic_colors = get_dynamic_colors(n_colors)
    node_colors = [dynamic_colors[coloring[node]] for node in graph.nodes()]
    labels = {node: f"{node}\nSlot {coloring[node] % 6 + 1}" for node in graph.nodes()}
    nodes = nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1400, edgecolors='black', linewidths=2)
    nx.draw_networkx_edges(graph, pos, width=2, alpha=0.5)
    nx.draw_networkx_labels(graph, pos, labels, font_size=13, font_weight='bold')
    plt.title(f"Exam Schedule Graph Coloring ({n_colors} Colors)", fontsize=18, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    app.run(debug=True)
