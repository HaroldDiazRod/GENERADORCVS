from flask import Flask, render_template, request, send_file, render_template_string
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from io import BytesIO
import os
import webbrowser
import threading
from googletrans import Translator

app = Flask(__name__)

@app.route('/')
def index():
    html_content = '''
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Generador de CV</title>
        <link rel="stylesheet" href="/static/styles.css">
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            form {
                max-width: 720px; /* Ajuste del ancho del formulario */
                margin: auto;
                padding: 1em;
                background: #f9f9f9;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                overflow-y: auto;
            }
            input[type="text"], input[type="email"], input[type="file"], textarea {
                width: 95%; /* Ajuste del ancho de las barras para escribir */
                padding: 0.5em; /* Ajuste del padding */
                margin: 0.4em 0; /* Ajuste del margen */
                box-sizing: border-box;
            }
            textarea {
                height: 100px;
            }
            label {
                display: block;
                margin-bottom: 0.4em; /* Ajuste del margen */
                font-weight: bold;
            }
            button {
                padding: 0.7em;
                color: #fff;
                background-color: #007BFF;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            .subgroup {
                margin-top: 1em;
                padding: 1em;
                background: #e9e9e9;
                border-radius: 5px;
                position: relative;
            }
            .subgroup label {
                margin-top: 0.4em; /* Ajuste del margen */
            }
            .function-container, .achievement-container {
                display: flex;
                align-items: center;
                margin-bottom: 0.4em; /* Ajuste del margen */
            }
            .function-container input, .achievement-container input {
                flex: 1;
            }
            .function-container button, .achievement-container button {
                margin-left: 0.5em;
                background-color: red;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .function-container button:hover, .achievement-container button:hover {
                background-color: darkred;
            }
            .remove-experience-btn, .remove-education-btn {
                position: absolute;
                top: 10px;
                right: 10px;
                background-color: red;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .remove-experience-btn:hover, .remove-education-btn:hover {
                background-color: darkred;
            }
        </style>
        <script>
            let experienceCount = 1;

            function addFunction(experienceId) {
                const functionsDiv = document.getElementById('functions_' + experienceId);
                const functionCount = functionsDiv.getElementsByClassName('function-container').length;

                if (functionCount < 10) {
                    const newFunctionDiv = document.createElement('div');
                    newFunctionDiv.className = 'function-container';
                    newFunctionDiv.innerHTML = `
                        <input type="text" name="job_function_${experienceId}_${functionCount}" placeholder="Función ${functionCount + 1}">
                        <button type="button" onclick="removeFunction(this)">X</button>
                    `;
                    functionsDiv.appendChild(newFunctionDiv);
                } else {
                    alert('Se permite un máximo de 10 funciones.');
                }
            }

            function removeFunction(button) {
                const functionsDiv = button.parentElement.parentElement;
                const functionCount = functionsDiv.getElementsByClassName('function-container').length;
                if (functionCount > 1) {
                    functionsDiv.removeChild(button.parentElement);
                } else {
                    alert('Debe haber al menos una función.');
                }
            }

            function addAchievement(experienceId) {
                const achievementsDiv = document.getElementById('achievements_' + experienceId);
                const achievementCount = achievementsDiv.getElementsByClassName('achievement-container').length;

                if (achievementCount < 10) {
                    const newAchievementDiv = document.createElement('div');
                    newAchievementDiv.className = 'achievement-container';
                    newAchievementDiv.innerHTML = `
                        <input type="text" name="job_achievement_${experienceId}_${achievementCount}" placeholder="Logro ${achievementCount + 1}">
                        <button type="button" onclick="removeAchievement(this)">X</button>
                    `;
                    achievementsDiv.appendChild(newAchievementDiv);
                } else {
                    alert('Se permite un máximo de 10 logros.');
                }
            }

            function removeAchievement(button) {
                const achievementsDiv = button.parentElement.parentElement;
                const achievementCount = achievementsDiv.getElementsByClassName('achievement-container').length;
                if (achievementCount > 1) {
                    achievementsDiv.removeChild(button.parentElement);
                } else {
                    alert('Debe haber al menos un logro.');
                }
            }

            function addExperience() {
                const experiencesDiv = document.getElementById('experiences');
                const experienceId = experienceCount;
                if (experienceCount < 8) {
                    const newExperienceDiv = document.createElement('div');
                    newExperienceDiv.className = 'subgroup';
                    newExperienceDiv.id = `experience_${experienceId}`;
                    newExperienceDiv.innerHTML = `
                        <button type="button" class="remove-experience-btn" onclick="confirmRemoveExperience(${experienceId})">X</button>
                        <label>EXPERIENCIA PROFESIONAL ${experienceId + 1}</label>
                        <label for="job_title_${experienceId}">Puesto laboral:</label>
                        <input type="text" id="job_title_${experienceId}" name="job_title_${experienceId}"><br>
                        <label for="company_name_${experienceId}">Nombre de empresa:</label>
                        <input type="text" id="company_name_${experienceId}" name="company_name_${experienceId}"><br>
                        <label for="job_city_country_${experienceId}">Ciudad, país:</label>
                        <input type="text" id="job_city_country_${experienceId}" name="job_city_country_${experienceId}" value="Trujillo, Perú"><br>
                        <label for="job_start_end_${experienceId}">Mes y año inicio - Mes y año fin:</label>
                        <input type="text" id="job_start_end_${experienceId}" name="job_start_end_${experienceId}"><br>
                        <label for="job_functions_${experienceId}">Funciones:</label>
                        <div id="functions_${experienceId}">
                            <div class="function-container">
                                <input type="text" name="job_function_${experienceId}_0" placeholder="Función 1">
                                <button type="button" onclick="removeFunction(this)">X</button>
                            </div>
                        </div>
                        <button type="button" class="add-function-btn" onclick="addFunction(${experienceId})">Agregar función</button><br>
                        <label for="job_achievements_${experienceId}">Logros:</label>
                        <div id="achievements_${experienceId}">
                            <div class="achievement-container">
                                <input type="text" name="job_achievement_${experienceId}_0" placeholder="Logro 1">
                                <button type="button" onclick="removeAchievement(this)">X</button>
                            </div>
                        </div>
                        <button type="button" class="add-achievement-btn" onclick="addAchievement(${experienceId})">Agregar logro</button><br>
                    `;
                    experiencesDiv.appendChild(newExperienceDiv);
                    experienceCount++;
                } else {
                    alert('Se permite un máximo de 8 experiencias profesionales.');
                }
            }

            function confirmRemoveExperience(experienceId) {
                if (confirm('¿Seguro que quieres borrar esta Experiencia profesional?')) {
                    removeExperience(experienceId);
                }
            }

            function removeExperience(experienceId) {
                const experiencesDiv = document.getElementById('experiences');
                const experienceDiv = document.getElementById(`experience_${experienceId}`);
                experiencesDiv.removeChild(experienceDiv);
                experienceCount--;
            }
            let educationCount = 1;

            function addEducation() {
                const educationsDiv = document.getElementById('educations');
                const educationId = educationCount;
                if (educationCount < 8) {
                    const newEducationDiv = document.createElement('div');
                    newEducationDiv.className = 'subgroup';
                    newEducationDiv.id = 'education_' + educationId;
                    newEducationDiv.innerHTML = `
                        <button type="button" class="remove-education-btn" style="background-color: red; color: white; position: absolute; right: 10px;" onclick="confirmRemoveEducation(${educationId})">X</button>
                        <label>EDUCACIÓN ${educationId + 1}</label>
                        <label for="university_${educationId}">Universidad:</label>
                        <input type="text" id="university_${educationId}" name="university_${educationId}"><br>
                        <label for="career_${educationId}">Carrera profesional:</label>
                        <input type="text" id="career_${educationId}" name="career_${educationId}"><br>
                        <label for="education_city_country_${educationId}">Ciudad, país:</label>
                        <input type="text" id="education_city_country_${educationId}" name="education_city_country_${educationId}" value="Trujillo, Perú"><br>
                        <label for="education_start_end_${educationId}">Mes y año inicio - Mes y año fin:</label>
                        <input type="text" id="education_start_end_${educationId}" name="education_start_end_${educationId}"><br>
                    `;
                    educationsDiv.appendChild(newEducationDiv);
                    educationCount++;
                } else {
                    alert('Se permite un máximo de 8 educaciones.');
                }
            }

            function confirmRemoveEducation(educationId) {
                if (confirm('¿Seguro que quieres borrar esta Educación?')) {
                    removeEducation(educationId);
                }
            }

            function removeEducation(educationId) {
                const educationsDiv = document.getElementById('educations');
                const educationDiv = document.getElementById('education_' + educationId);
                educationsDiv.removeChild(educationDiv);
                educationCount--;
            }
        </script>
    </head>
    <body>
        <h1>Generador de CV AIESEC Trujillo 24.2</h1>
        <form action="/generate-cv" method="post" enctype="multipart/form-data">
            <label for="name">Nombre y Apellido:</label>
            <input type="text" id="name" name="name" required><br><br>
            <label for="profession">Profesión:</label>
            <input type="text" id="profession" name="profession"><br><br>
            <label for="city_country">Ciudad, país:</label>
            <input type="text" id="city_country" name="city_country" value="Trujillo, Perú"><br><br>
            <label for="email">Correo electrónico:</label>
            <input type="email" id="email" name="email"><br><br>
            <label for="phone">Teléfono:</label>
            <input type="text" id="phone" name="phone" value="+51 "><br><br>
            <label for="linkedin">LinkedIn:</label>
            <input type="text" id="linkedin" name="linkedin"><br><br>
            <label for="profile_summary">Resumen profesional:</label>
            <textarea id="profile_summary" name="profile_summary"></textarea><br><br>
            <label for="languages">Idiomas:</label>
            <input type="text" id="languages" name="languages"><br><br>
            <label for="profile_picture">Foto de perfil:</label>
            <input type="file" id="profile_picture" name="profile_picture" accept="image/*"><br><br>
            
            <!-- Experiencia Profesional -->
            <div id="experiences">
                <div class="subgroup">
                    <label>EXPERIENCIA PROFESIONAL</label>
                    <label for="job_title_0">Puesto laboral:</label>
                    <input type="text" id="job_title_0" name="job_title_0"><br>
                    <label for="company_name_0">Nombre de empresa:</label>
                    <input type="text" id="company_name_0" name="company_name_0"><br>
                    <label for="job_city_country_0">Ciudad, país:</label>
                    <input type="text" id="job_city_country_0" name="job_city_country_0" value="Trujillo, Perú"><br>
                    <label for="job_start_end_0">Mes y año inicio - Mes y año fin:</label>
                    <input type="text" id="job_start_end_0" name="job_start_end_0"><br>
                    <label for="job_functions_0">Funciones:</label>
                    <div id="functions_0">
                        <div class="function-container">
                            <input type="text" name="job_function_0_0" placeholder="Función 1">
                            <button type="button" onclick="removeFunction(this)">X</button>
                        </div>
                    </div>
                    <button type="button" class="add-function-btn" onclick="addFunction(0)">Agregar función</button><br>
                    <label for="job_achievements_0">Logros:</label>
                    <div id="achievements_0">
                        <div class="achievement-container">
                            <input type="text" name="job_achievement_0_0" placeholder="Logro 1">
                            <button type="button" onclick="removeAchievement(this)">X</button>
                        </div>
                    </div>
                    <button type="button" class="add-achievement-btn" onclick="addAchievement(0)">Agregar logro</button><br>
                </div>
            </div>
            <button type="button" onclick="addExperience()">Agregar experiencia profesional</button><br><br>

            <!-- Educación -->
            <div id="educations">
                <div class="subgroup">
                    <label>EDUCACIÓN</label>
                    <label for="university_0">Universidad:</label>
                    <input type="text" id="university_0" name="university_0"><br>
                    <label for="career_0">Carrera profesional:</label>
                    <input type="text" id="career_0" name="career_0"><br>
                    <label for="education_city_country_0">Ciudad, país:</label>
                    <input type="text" id="education_city_country_0" name="education_city_country_0" value="Trujillo, Perú"><br>
                    <label for="education_start_end_0">Mes y año inicio - Mes y año fin:</label>
                    <input type="text" id="education_start_end_0" name="education_start_end_0"><br>
                </div>
            </div>
            <button type="button" onclick="addEducation()">Agregar Educación</button><br><br>

            <!-- Información Adicional -->
            <div class="subgroup">
                <label>INFORMACIÓN ADICIONAL</label>
                <label for="volunteer">Voluntariado:</label>
                <input type="text" id="volunteer" name="volunteer"><br>
                <label for="certificates">Certificados:</label>
                <input type="text" id="certificates" name="certificates"><br>
                <label for="soft_skills">Habilidades blandas:</label>
                <input type="text" id="soft_skills" name="soft_skills"><br>
                <label for="hard_skills">Habilidades duras:</label>
                <input type="text" id="hard_skills" name="hard_skills"><br>
            </div>

            <button type="submit">Generar CV</button>
            <button type="submit" formaction="/generate-cv-en">Generar CV en inglés</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/generate-cv', methods=['POST'])
def generate_cv():
    name = request.form['name']
    profession = request.form.get('profession', '')
    city_country = request.form.get('city_country', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    linkedin = request.form.get('linkedin', '')
    profile_summary = request.form.get('profile_summary', '')
    languages = request.form.get('languages', '')
    profile_picture = request.files.get('profile_picture')

    # Educación
    educations = []
    for education_id in range(8):  # Máximo 8 educaciones
        university = request.form.get(f'university_{education_id}')
        if not university:
            continue  # Saltar esta educación si no tiene universidad

        career = request.form.get(f'career_{education_id}', '')
        education_city_country = request.form.get(f'education_city_country_{education_id}', 'Trujillo, Perú')
        education_start_end = request.form.get(f'education_start_end_{education_id}', '')

        educations.append({
            'university': university,
            'career': career,
            'education_city_country': education_city_country,
            'education_start_end': education_start_end,
        })

    # Información adicional
    volunteer = request.form.get('volunteer', '')
    certificates = request.form.get('certificates', '')
    soft_skills = request.form.get('soft_skills', '')
    hard_skills = request.form.get('hard_skills', '')

    experiences = []
    for experience_id in range(8):  # Máximo 8 experiencias
        job_title = request.form.get(f'job_title_{experience_id}')
        if not job_title:
            continue  # Saltar esta experiencia si no tiene un título laboral

        company_name = request.form.get(f'company_name_{experience_id}', '')
        job_city_country = request.form.get(f'job_city_country_{experience_id}', '')
        job_start_end = request.form.get(f'job_start_end_{experience_id}', '')

        job_functions = []
        job_achievements = []
        for key in request.form:
            if key.startswith(f'job_function_{experience_id}_'):
                job_functions.append(request.form[key])
            elif key.startswith(f'job_achievement_{experience_id}_'):
                job_achievements.append(request.form[key])

        experiences.append({
            'job_title': job_title,
            'company_name': company_name,
            'job_city_country': job_city_country,
            'job_start_end': job_start_end,
            'job_functions': [{'function': func} for func in job_functions],
            'job_achievements': [{'achievement': ach} for ach in job_achievements],
        })

    doc = DocxTemplate("CV1.docx")

    context = {
        'NAME_AND_SURNAME': name,
        'PROFESSION': profession,
        'CITY_COUNTRY_EMAIL_PHONE_LINKEDIN': f'{city_country} | {email} | {phone} | {linkedin}',
        'PROFILE_SUMMARY': profile_summary,
        'LANGUAGES': languages,
        'VOLUNTEER': volunteer,
        'CERTIFICATES': certificates,
        'SOFT_SKILLS': soft_skills,
        'HARD_SKILLS': hard_skills,
        'EXPERIENCES': experiences,
        'EDUCATIONS': educations,
    }

    if profile_picture:
        context['PROFILE_PICTURE'] = InlineImage(doc, BytesIO(profile_picture.read()), width=Mm(30))

    doc.render(context)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # Nombrar el archivo de salida basado en el nombre y apellido ingresado
    cv_filename = f'CV {name}.docx'

    return send_file(output, as_attachment=True, download_name=cv_filename)

@app.route('/generate-cv-en', methods=['POST'])
def generate_cv_en():
    name = request.form['name']
    profession = request.form.get('profession', '')
    city_country = request.form.get('city_country', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    linkedin = request.form.get('linkedin', '')
    profile_summary = request.form.get('profile_summary', '')
    languages = request.form.get('languages', '')
    profile_picture = request.files.get('profile_picture')

    # Educación
    educations = []
    for education_id in range(8):  # Máximo 8 educaciones
        university = request.form.get(f'university_{education_id}')
        if not university:
            continue  # Saltar esta educación si no tiene universidad

        career = request.form.get(f'career_{education_id}', '')
        education_city_country = request.form.get(f'education_city_country_{education_id}', 'Trujillo, Perú')
        education_start_end = request.form.get(f'education_start_end_{education_id}', '')

        educations.append({
            'university': university,
            'career': career,
            'education_city_country': education_city_country,
            'education_start_end': education_start_end,
        })

    # Información adicional
    volunteer = request.form.get('volunteer', '')
    certificates = request.form.get('certificates', '')
    soft_skills = request.form.get('soft_skills', '')
    hard_skills = request.form.get('hard_skills', '')

    experiences = []
    for experience_id in range(8):  # Máximo 8 experiencias
        job_title = request.form.get(f'job_title_{experience_id}')
        if not job_title:
            continue  # Saltar esta experiencia si no tiene un título laboral

        company_name = request.form.get(f'company_name_{experience_id}', '')
        job_city_country = request.form.get(f'job_city_country_{experience_id}', '')
        job_start_end = request.form.get(f'job_start_end_{experience_id}', '')

        job_functions = []
        job_achievements = []
        for key in request.form:
            if key.startswith(f'job_function_{experience_id}_'):
                job_functions.append(request.form[key])
            elif key.startswith(f'job_achievement_{experience_id}_'):
                job_achievements.append(request.form[key])

        experiences.append({
            'job_title': job_title,
            'company_name': company_name,
            'job_city_country': job_city_country,
            'job_start_end': job_start_end,
            'job_functions': [{'function': func} for func in job_functions],
            'job_achievements': [{'achievement': ach} for ach in job_achievements],
        })

    # Crear instancia de traductor
    translator = Translator()

    # Traducir campos
    name_en = translator.translate(name, dest='en').text
    profession_en = translator.translate(profession, dest='en').text
    city_country_en = translator.translate(city_country, dest='en').text
    profile_summary_en = translator.translate(profile_summary, dest='en').text
    languages_en = translator.translate(languages, dest='en').text

    educations_en = [{
        'university': translator.translate(edu['university'], dest='en').text,
        'career': translator.translate(edu['career'], dest='en').text,
        'education_city_country': translator.translate(edu['education_city_country'], dest='en').text,
        'education_start_end': translator.translate(edu['education_start_end'], dest='en').text,
    } for edu in educations]

    volunteer_en = translator.translate(volunteer, dest='en').text
    certificates_en = translator.translate(certificates, dest='en').text
    soft_skills_en = translator.translate(soft_skills, dest='en').text
    hard_skills_en = translator.translate(hard_skills, dest='en').text

    experiences_en = [{
        'job_title': translator.translate(exp['job_title'], dest='en').text,
        'company_name': translator.translate(exp['company_name'], dest='en').text,
        'job_city_country': translator.translate(exp['job_city_country'], dest='en').text,
        'job_start_end': translator.translate(exp['job_start_end'], dest='en').text,
        'job_functions': [{'function': translator.translate(func['function'], dest='en').text} for func in exp['job_functions']],
        'job_achievements': [{'achievement': translator.translate(ach['achievement'], dest='en').text} for ach in exp['job_achievements']],
    } for exp in experiences]

    doc = DocxTemplate("CV2.docx")

    context = {
        'NAME_AND_SURNAME': name_en,
        'PROFESSION': profession_en,
        'CITY_COUNTRY_EMAIL_PHONE_LINKEDIN': f'{city_country_en} | {email} | {phone} | {linkedin}',
        'PROFILE_SUMMARY': profile_summary_en,
        'LANGUAGES': languages_en,
        'EDUCATIONS': educations_en,
        'VOLUNTEER': volunteer_en,
        'CERTIFICATES': certificates_en,
        'SOFT_SKILLS': soft_skills_en,
        'HARD_SKILLS': hard_skills_en,
        'EXPERIENCES': experiences_en,
    }

    if profile_picture:
        picture_filename = f'profile_picture_{name}.jpg'
        profile_picture.save(picture_filename)
        context['PROFILE_PICTURE'] = InlineImage(doc, picture_filename, width=Mm(40))

    doc.render(context)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # Eliminar la imagen guardada
    if profile_picture:
        os.remove(picture_filename)

    # Nombrar el archivo de salida basado en el nombre y apellido ingresado
    cv1_filename = f'CV ENG {name}.docx'

    return send_file(output, as_attachment=True, download_name=cv1_filename)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1, open_browser).start() 
    app.run(debug=True, use_reloader=False)
