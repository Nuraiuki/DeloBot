from django.db import models

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True, null=False)
    password = models.CharField(max_length=255)

    def __str__(self):
        return f"User: {self.username}"
class Anketa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    age = models.IntegerField(null=False)
    city = models.CharField(max_length=255, null=False)
    gender = models.CharField(max_length=20, null=False)
    file_url = models.CharField(max_length=255, null=False)
    phone_number = models.CharField(max_length=230, blank=True)
    job = models.CharField(max_length=20, null=False)

    def __str__(self):
        return f"{self.name}'s Anketa"
class JobSeeker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    skill = models.CharField(max_length=255)
    format = models.CharField(max_length=255)
    experience_j = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)

class Employer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    vacancy_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    skills = models.TextField()
    short_description = models.TextField()
    job_description = models.TextField()
    format_e = models.CharField(max_length=255)
    experience_e = models.CharField(max_length=255)
    salary = models.CharField(max_length=255)
    spec = models.CharField(max_length=255)

class Feedback_table(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    vacancy_id = models.ForeignKey(Employer, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    feedback_text = models.TextField()
 
    def __str__(self):
        return self.field_name