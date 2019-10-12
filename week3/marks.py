students = [
    {
        "name": "Matt",
        "homework": [90.0, 97.0, 75.0, 92.0],
        "quizzes": [88.0, 40.0, 94.0],
        "tests": [75.0, 90.0],
    },
    {
        "name": "Mich",
        "homework": [100.0, 92.0, 98.0, 100.0],
        "quizzes": [82.0, 83.0, 91.0],
        "tests": [89.0, 97.0],
    },
    {
        "name": "Mark",
        "homework": [0.0, 87.0, 75.0, 22.0],
        "quizzes": [0.0, 75.0, 78.0],
        "tests": [100.0, 100.0],
    }
]

if __name__ == '__main__':
    homework = 0
    quizzes = 0
    tests = 0
    for people in students:
        homework += sum(people['homework'])/len(people['homework'])
        quizzes += sum(people['quizzes'])/len(people['quizzes'])
        tests += sum(people['tests'])/len(people['tests'])
    
    print(f"Average homework mark: {homework/len(students):0.2f}")
    print(f"Average quiz mark: {quizzes/len(students):0.2f}")
    print(f"Average test mark: {tests/len(students):0.2f}")