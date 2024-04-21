import subprocess
import os
import glob
import re
from django.shortcuts import render, redirect
from django.http import HttpResponse  # RepositoryForm'un tanımlanmış olması gerekiyor.
from .models import JavaFile  # JavaFile modelinizin tanımlanmış olması gerekiyor.
from django.http import HttpResponse
from .forms import GithubRepoForm
import tempfile
import shutil

def home(request):
    if request.method == 'POST':
        form = GithubRepoForm(request.POST)
        if form.is_valid():
            # Form geçerliyse ve URL doğruysa, başka işlemler yap veya başarı sayfasına yönlendir
            # Bu örnekte, kullanıcıyı aynı sayfada tutup bir başarı mesajı gösterelim
            return render(request, 'app/home.html', {'form': form, 'message': 'Form başarıyla gönderildi!'})
        else:
            # Form geçersizse, formu ve hataları göstererek aynı sayfayı yeniden render et
            return render(request, 'app/home.html', {'form': form})
    else:
        form = GithubRepoForm()
    return render(request, 'app/home.html', {'form': form})

def success(request):
    return HttpResponse('<h1>İşlem Başarılı!</h1>')

def submit_repository(request):
    if request.method == 'POST':
        form = GithubRepoForm(request.POST)
        if form.is_valid():
            repo_url = form.cleaned_data['repo_url']

            # URL'yi session'a kaydet
            request.session['repo_url'] = repo_url

            # Repository klonlama ve analiz işlemi
            clone_repository(repo_url)

            # Sonuçları göstermek için show_results view'ına yönlendir
            return redirect('show_results')
    else:
        form = GithubRepoForm()
    return render(request, 'app/submit_repository.html', {'form': form})



def clone_repository(repo_url):
    print(f"Klonlanıyor: {repo_url}")
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.call(['git', 'clone', repo_url, temp_dir])
        java_files = glob.glob(os.path.join(temp_dir, '**/*.java'), recursive=True)
        for file_path in java_files:
            analyze_java_file(file_path, repo_url)  # repo_url parametresini buraya ekliyoruz




def count_class_presence(file_lines):
    """Dosyada 'class' anahtar kelimesinin olup olmadığını kontrol et."""
    return any('class' in line for line in file_lines)

def count_code_lines(file_lines):
    """Kod satırlarının sayısını hesapla."""
    code_lines = sum(1 for line in file_lines if line.strip() and not line.strip().startswith(('*', '/')))
    return code_lines

def count_functions(file_lines):
    """Fonksiyon sayısını hesapla."""
    function_count = sum(1 for line in file_lines if re.search(r'\b(public|protected|private)?\s+\w+\s*\([^)]*\)\s*\{', line) or re.search(r'\b(public|protected|private)\s+\w+\s*\([^)]*\)', line))
    return function_count

def calculate_comment_deviation(javadoc_comment_count, other_comment_count, function_count, code_lines):
    """Yorum sapma yüzdesini hesapla."""
    if function_count > 0:
        YG = (javadoc_comment_count + other_comment_count) * 0.8 / function_count
        YH = code_lines * 0.3 / function_count
        return ((100 * YG) / YH) - 100
    return 0.0

def count_other_comments(file_lines):
    in_other_comment = False
    other_comment_count = 0
    for line in file_lines:
        stripped_line = line.strip()

        # Tek satırlık yorumlar
        if stripped_line.startswith("//"):
            other_comment_count += 1
        elif "/*" in stripped_line and not stripped_line.startswith("/**"):
            # Çok satırlık yorumların tek satırda başlayıp bitmesi durumu
            if "*/" in stripped_line:
                other_comment_count += 1
            else:
                in_other_comment = True
                other_comment_count += 1
        elif "*/" in stripped_line:
            in_other_comment = False
        elif in_other_comment:
            continue
        elif "//" in stripped_line:
            other_comment_count += 1
            
    return other_comment_count








def count_javadoc_comments(file_lines):
    """Javadoc yorum satırlarının sayısını hesapla."""
    in_javadoc_comment = False
    javadoc_comment_count = 0
    for line in file_lines:
        stripped_line = line.strip()
        if stripped_line.startswith('/**'):
            in_javadoc_comment = True
            continue  # Javadoc yorumunun başlangıcı sayılmaz
        elif in_javadoc_comment:
            if stripped_line.endswith('*/'):
                in_javadoc_comment = False
                continue  # Javadoc yorumunun bitişi sayılmaz
            javadoc_comment_count += 1
    return javadoc_comment_count




def analyze_java_file(file_path, repo_url):
    print(f"Analiz ediliyor: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not count_class_presence(lines):
            print("Dosyada 'class' anahtar kelimesi bulunamadı, analiz edilmiyor.")
            return
        
        loc = len(lines)
        code_lines = count_code_lines(lines)
        function_count = count_functions(lines)
        javadoc_comment_count = count_javadoc_comments(lines)
        other_comment_count = count_other_comments(lines)
        comment_deviation_percentage = calculate_comment_deviation(javadoc_comment_count, other_comment_count, function_count, code_lines)

        JavaFile.objects.update_or_create(
            file_name=os.path.basename(file_path),
            repo_url=repo_url,  # URL bilgisini buraya ekleyin.
            defaults={
                'loc': loc,
                'code_line_count': code_lines,
                'javadoc_comment_count': javadoc_comment_count,
                'other_comment_count': other_comment_count,
                'function_count': function_count,
                'comment_deviation_percentage': comment_deviation_percentage,
            }
        )
        print(f"Kaydedildi: {os.path.basename(file_path)}")

    except Exception as e:
        print(f"Hata dosya analizi sırasında: {e}")



def show_results(request):
    # Session'dan repo_url'i al
    repo_url = request.session.get('repo_url', None)

    # repo_url'e göre JavaFile nesnelerini filtrele
    if repo_url:
        java_files = JavaFile.objects.filter(repo_url=repo_url)
    else:
        java_files = JavaFile.objects.none()  # Eğer URL yoksa boş bir queryset döndür

    return render(request, 'app/show_results.html', {'java_files': java_files})

def show_all_results(request):
    java_files = JavaFile.objects.all()  # Tüm JavaFile kayıtlarını çek
    return render(request, 'app/show_all_files.html', {'java_files': java_files})

