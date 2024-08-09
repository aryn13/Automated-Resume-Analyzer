from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('home/', views.home, name='automated_resume-home'),
    path('home/success/', views.resume_success, name="automated_resume-success"),
    path('home/instructions/', views.display_instructions, name="automated_resume_instructions"),
    path('home/questions/', views.questions_to_display, name="automated_resume-questions-page"),
    path('home/render_questions/', views.render_questions, name="automated_resume-render-questions"),
    path('save_answer/', views.save_answer, name='save_answer'),
    path('home/results/', views.display_result, name="automated_resume_display_result"),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='automated_resume/reset_password_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('admin-dashboard/', views.admin_home, name='admin_dashboard'),
    path('home/resume/review/', views.review_quiz, name="review_quiz"),
    # path('home/resume/question2', views.questions_to_display2(), name="automa")
]
