class Person:
    def __init__(self, gender, age, head_height, leg_height, shoulders_hips):
        self.gender = gender
        self.age = age
        self.headHeight = head_height
        self.ratioLegs = leg_height
        self.ratioSH = shoulders_hips

    def __repr__(self):
        return "Person('{}', {}, {}, {}, {})".format(self.gender, self.age, self.headHeight, self.ratioLegs, self.ratioSH)
