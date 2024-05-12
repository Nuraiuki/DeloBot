from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User, Anketa, JobSeeker, Employer, Feedback_table

admin.site.register(User)

class EmployerResource(resources.ModelResource):
    class Meta:
        model = Employer
        exclude = ('id',)
        import_id_fields = []

@admin.register(Employer)
class Employeradmin(ImportExportModelAdmin):
    resource_class = EmployerResource
    list_display = ['user','job_title','vacancy_id','company_name','industry','skills','short_description','job_description','format_e','experience_e','salary','spec']
    search_fields = ['job_title__istartswith','spec']
    list_editable = ['job_title','industry','skills','short_description','job_description','format_e','experience_e','salary','spec']
    ordering = ['vacancy_id']

# @admin.site.register(Feedback_table)

@admin.register(Anketa)
class Anketaadmin(admin.ModelAdmin):
    list_display = ['name','age','city','gender','file_url','phone_number','job']
    search_fields = ['name__istartswith','job']
    list_editable = ['age','city','file_url','job']
    ordering = ['job']

@admin.register(JobSeeker)
class JobSeekeradmin(admin.ModelAdmin):
    list_display = ['user_id','category','skill','format','experience_j','salary']
    search_fields = ['salary','skill__istartswith','category__istartswith']
    list_editable = ['category','skill','format','experience_j','salary']
    ordering = ['salary']
    
@admin.register(Feedback_table)
class Feedback_tableadmin(admin.ModelAdmin):
    list_display = ['action','feedback_text']
    ordering = ['action']

