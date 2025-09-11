import pandas as pd



# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Define file paths
# courses_path = os.path.join(BASE_DIR, "data", "courses.csv")
# students_path = os.path.join(BASE_DIR, "data", "students.csv")

# # Read CSV files
# courses_df = pd.read_csv(courses_path)
# students_df = pd.read_csv(students_path)

# # Print data for testing
# print("\n=== Courses Data ===")
# print(courses_df.head())

# print("\n=== Students Data ===")
# print(students_df.head())


file_path = r"C:\Users\Jyothiswar Reddy\OneDrive\Desktop\courses.csv"
df = pd.read_csv(file_path)
print(df)


file_path = r"C:\Users\Jyothiswar Reddy\OneDrive\Desktop\students.csv"
df = pd.read_csv(file_path)
print(df)
