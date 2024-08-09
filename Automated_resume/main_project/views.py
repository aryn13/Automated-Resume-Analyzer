import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.utils.safestring import mark_safe
from django.db import DatabaseError
import os
from .forms import ResumeForm, AdminLoginForm, CustomSetPasswordForm, QuestionForm, ResetPasswordDone
from .models import ResumeData, QuestionsData, ResultData, AdminData, SelectedOptionDatabase
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.urls import reverse_lazy
from .utils import extract_skills, extract_question, parse_questions, extract_correct_answers, save_to_excel, cutoff


def six_months_timer(quiz_date) -> bool:
    current_date = datetime.now()
    six_months_ago = current_date - timedelta(days=6*30)
    six_months_ago = six_months_ago.date()
    if six_months_ago >= quiz_date:
        return True
    else:
        return False


@csrf_exempt
def save_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        test_id = data.get('test_id')

        try:
            question_data = QuestionsData.objects.get(id=question_id, TestID=test_id)
            is_correct = question_data.CorrectOption == selected_option
            ResultData.objects.create(
                TestID=question_data,
                Marks=1 if is_correct else 0,
                Result=is_correct
            )
            return JsonResponse({"status": "success"})
        except QuestionsData.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Question not found"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                admin_user = AdminData.objects.get(email=email)
                if check_password(password, admin_user.password):
                    return redirect("admin_dashboard")
                else:
                    messages.error(request, 'Invalid password')
                    return render(request, 'automated_resume/login.html', {'form': form})
            except AdminData.DoesNotExist:
                messages.error(request, 'Admin user does not exist')
    else:
        form = AdminLoginForm()
    return render(request, 'automated_resume/login.html', {'form': form})


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['Admin_Email'] = email

        try:
            admin = AdminData.objects.get(email=email)
        except AdminData.DoesNotExist:
            messages.error(request, 'No admin with this email exists.')
            return redirect('reset_password')

        token = default_token_generator.make_token(admin)
        uid = urlsafe_base64_encode(force_bytes(admin.pk))

        reset_link = request.build_absolute_uri(
            reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        message = render_to_string('automated_resume/password_reset_email.html', {
            'user': admin,
            'reset_link': reset_link,
            'site_name': "Resume Analyser",
        })

        send_mail(
            'Password Reset Request',
            message,
            'from@example.com',
            [email],
            fail_silently=False,
        )
        return redirect('password_reset_done')

    return render(request, 'automated_resume/reset_password.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = AdminData.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, AdminData.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                confirm_password = form.cleaned_data['new_password2']
                if new_password == confirm_password:
                    user.password = make_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been set. You can log in now.')
                    return redirect('password_reset_complete')
                else:
                    messages.error(request, 'Passwords do not match.')
        else:
            form = CustomSetPasswordForm(user, request.GET)
    else:
        messages.error(request, 'The reset password link is no longer valid.')
        return redirect('password_reset_done')

    return render(request, 'automated_resume/reset_password_confirm.html', {'form': form})


def password_reset_complete(request):
    return render(request, 'automated_resume/reset_password_complete.html')


def admin_home(request):
    return render(request, 'automated_resume/dashboard.html')


# Create your views here.
def home(request):
    print("Reached here")
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            request.session["email"] = email
            phone = form.cleaned_data['phone']
            request.session["phone"] = phone
            dob = form.cleaned_data['dob']
            resume = request.FILES['resume']
            fs = FileSystemStorage()
            global resume_path
            resume_path = fs.save(resume.name, resume)
            print("About to extract skills")
            level, skills_str = extract_skills(resume_path)
            print("skills extracted")
            resume_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'dob': dob,
                'path': os.path.join(os.path.dirname(os.path.realpath(__file__)), resume_path),
                'skills': skills_str.replace("\n", ""),
                'candidate_experience': level
            }
            try:
                ResumeData.objects.create(
                    name=resume_data['name'],
                    email=resume_data['email'],
                    phone=resume_data['phone'],
                    dob=resume_data['dob'],
                    pdf_path=resume_data['path'],
                    skills=resume_data['skills'],
                    candidate_experience=resume_data['candidate_experience'],
                    date_of_quiz=datetime.now()
                )

                save_to_excel([name, email, phone, dob, resume_path])
                request.session['skills_str'] = skills_str
                request.session['level'] = level
                return redirect('automated_resume_instructions')
            except IntegrityError:
                instance = ResumeData.objects.get(email=email)
                database_date = instance.date_of_quiz
                if six_months_timer(database_date):
                    instance = ResumeData.objects.filter(email=email)
                    instance.delete()
                    ResumeData.objects.create(
                        name=resume_data['name'],
                        email=resume_data['email'],
                        phone=resume_data['phone'],
                        dob=resume_data['dob'],
                        pdf_path=resume_data['path'],
                        skills=resume_data['skills'],
                        candidate_experience=resume_data['candidate_experience'],
                        date_of_quiz=datetime.now()
                    )

                    save_to_excel([name, email, phone, dob, resume_path])
                    request.session['skills_str'] = skills_str
                    request.session['level'] = level
                    return redirect('automated_resume_instructions')
                else:
                    messages.info(request, mark_safe("User Already Exists in the Database Please try again after 6 "
                                                     "months, please <a href='resume/review/'> click here </a> to "
                                                     "review you quiz"))
    else:
        form = ResumeForm()
    return render(request, "automated_resume/test.html", {"form": form})


def display_instructions(request):
    return render(request, "automated_resume/instructions.html")


def resume_success(request):
    print(request.method)
    skills = request.session.get("skills_str", "")
    candidate_experience = request.session.get("level", "")
    print("skills in resume success: ", skills)
    questionnaire = extract_question(extracted_skills=skills, experience_level=candidate_experience)
    print("Questionnaire in resume_success: ", questionnaire)
    questions_dict = parse_questions(questionnaire)
    print("question dict in resume success: ", questions_dict)
    answer_dict, questions_dict = extract_correct_answers(questions_dict)
    print("answer_dict in resume_success function: \n", answer_dict)
    resume_data = ResumeData.objects.latest('id')
    correct_answers = []
    for count, (question, options_dict) in enumerate(questions_dict.items()):
        print("question to reference in answerdict: ", question)
        correct_answer = answer_dict.get(question, "")
        correct_answers.append(correct_answer)
        request.session['correct_answers_list'] = correct_answers
        options_list = [text for text in options_dict.values()]
        options_string = "~~ ".join(options_list)

        QuestionsData.objects.create(
            TestID=resume_data,
            Questions=question,
            Options=options_string,
            CorrectOption=correct_answer.replace("**", "").replace("****", "")
        )

    # Store the primary key of the resume_data instance in session
    q_pk_list = [item.pk for item in QuestionsData.objects.all()]
    request.session["Latest_test_taker_id"] = resume_data.pk
    request.session['Question_pk_list'] = q_pk_list
    request.session["selected_options_list"] = []
    request.session['questions_dict'] = questions_dict
    return redirect('automated_resume-questions-page')


def questions_to_display(request):
    if request.method == "POST":
        current_question = request.session.get("current_question", "")
        list_of_options = request.session.get("Options_List", [])
        form = QuestionForm(request.POST, question=current_question, options=list_of_options)
        if form.is_valid():
            selected_option = form.cleaned_data.get('option')
            selected_option_list = request.session.get("selected_options_list")
            if selected_option == "":
                selected_option_list.append("")
            else:
                selected_option_list.append(selected_option)
            request.session.save()

        else:
            print(form.errors)
            print("option: ", form.cleaned_data.get("option"))
            selected_option_list = request.session.get("selected_options_list")
            selected_option_list.append("")
            request.session.save()
            # You can process the selected option here, like saving it to the session or database
            # For example:
            # request.session['selected_option'] = selected_option
        return redirect('automated_resume-questions-page')  # Redirect to the next question or another page
    questions_dict = request.session.get('questions_dict', {})
    if not questions_dict:
        return redirect('automated_resume_display_result')

    question_str = ""
    option_str = ""
    for question, options in questions_dict.items():
        question_str += question
        for text in options.values():
            text = text.replace("**", "").replace("****", "").replace("✔️", "").replace("✅", "").replace("✔", "").replace("✓", "").strip()
            option_str += "~" + text
        questions_dict.pop(question)
        request.session.save()
        request.session['current_question'] = question_str
        request.session['current_options'] = option_str
        break
    return redirect('automated_resume-render-questions')


def render_questions(request):
    current_question = request.session.get("current_question", "")
    current_options = request.session.get("current_options", "")
    options_to_pass = [(i, option) for i, option in enumerate(current_options.split('~')) if option != ""]
    request.session['Options_List'] = options_to_pass
    form = QuestionForm(question=current_question, options=options_to_pass)
    return render(request, "automated_resume/questions.html", {"form": form, "timer": 30})


def display_result(request):
    marks = 0.0
    latest_test_taker_id = request.session.get("Latest_test_taker_id")
    latest_test_taker = ResumeData.objects.get(pk=latest_test_taker_id)
    question_objects_list = QuestionsData.objects.filter(TestID=latest_test_taker)
    selected_options_list = request.session.get("selected_options_list", [])
    correct_option_list = request.session.get("correct_answers_list", [])
    print(selected_options_list)
    print("Selected_options length: ", len(selected_options_list))
    selected_options_list_updated = converter(selected_options_list)

    for index, question_object in enumerate(question_objects_list):
        SelectedOptionDatabase.objects.create(
            selected_id=question_object,
            selectOption=selected_options_list_updated[index]
        )
        if correct_option_list[index] == selected_options_list_updated[index]:
            marks += 1
    ResultData.objects.create(
        TestID=latest_test_taker,
        Marks=marks,
        Result=cutoff <= marks
    )
    percent = round((marks / len(question_objects_list)) * 100, 0)
    context = {
        "marks": marks,
        "percentage": percent,
        "cutoff": cutoff,
    }
    return render(request, "automated_resume/Results.html", context=context)


def converter(sel_list):
    new_list = []
    converter_dict = {
        "1": "a",
        "2": "b",
        "3": "c",
        "4": "d",
        "5": "e",
        "6": "f",
        "7": "g",
        "": "nil"
    }
    for i in sel_list:
        if i == 'nil':
            new_list.append('nil')
        else:
            new_list.append(converter_dict.get(i, 'nil'))
    return new_list


def selected_option_text(charac, selected_list) -> str:
    char_dic = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "nil": None
    }
    try:
        return selected_list[char_dic[charac]]
    except KeyError:
        return ""


def review_quiz(request):
    email = request.session.get("email")
    phone = request.session.get("phone")
    resume_object = ResumeData.objects.get(email=email, phone=phone)
    question_objects_list = QuestionsData.objects.filter(TestID=resume_object)
    selected_options_list = SelectedOptionDatabase.objects.filter(selected_id__TestID=resume_object)

    review_data = []
    total_questions = len(question_objects_list)
    correct_answers = 0

    for question_obj, selected_option_obj in zip(question_objects_list, selected_options_list):
        is_correct = question_obj.CorrectOption == selected_option_obj.selectOption
        if is_correct:
            correct_answers += 1

        review_data.append({
            "question": question_obj.Questions,
            "options": question_obj.Options.replace("****", "").split("~~ "),
            "selected_option": selected_option_obj.selectOption,
            "correct_option": question_obj.CorrectOption,
            "selected_option_value": selected_option_text(selected_option_obj.selectOption,
                                                           question_obj.Options.replace("****", "").split("~~ ")),
            "correct_option_value": selected_option_text(question_obj.CorrectOption,
                                                           question_obj.Options.replace("****", "").split("~~ ")),
            "is_correct": is_correct
        })
    print("Questions Data:", review_data)
    result_percentage = (correct_answers / total_questions) * 100
    print("Resume Object:", resume_object)
    print("Question Objects List:", question_objects_list)
    print("Selected Options List:", selected_options_list)

    for question_obj, selected_option_obj in zip(question_objects_list, selected_options_list):
        print("Processing Question:", question_obj.Questions)
        print("Selected Option:", selected_option_obj.selectOption)
        # Add the rest of the loop code here

    context = {
        "review_data": review_data,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "result_percentage": result_percentage
    }
    return render(request, "automated_resume/review.html", context)


