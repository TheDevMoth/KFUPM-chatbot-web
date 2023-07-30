from enum import Enum

class Category(Enum):
    """Category of questions"""
    FOLLOWUP = 1
    SCHEDULE = 2
    RULES = 3
    REGISTRATION = 4
    SMALLTALK = 5
    UNRELATED = 6
    OTHER = 7

CATE_STRING = {
    Category.FOLLOWUP: "Follow up question",
    Category.SCHEDULE: "Specific dates on the academic calendar",
    Category.RULES: "University rules, regulations, and policies",
    Category.REGISTRATION: "University registration and admission",
    Category.SMALLTALK: "Small talk or greeting",
    Category.UNRELATED: "Unrelated to kfupm",
    Category.OTHER: "None of the above"
}

if __name__ == "__main__":
    print(CATE_STRING.values())