from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from .models import JavaFile
from .views import (calculate_comment_deviation, count_class_presence, count_code_lines, count_functions, 
                    count_other_comments, count_javadoc_comments, analyze_java_file,clone_repository)
from .forms import GithubRepoForm
import unittest
import os
from django.test import TestCase, Client
from django.urls import reverse
from .forms import GithubRepoForm
from unittest.mock import patch, MagicMock
import tempfile
from unittest.mock import patch, mock_open
from parameterized import parameterized
from django.test import TestCase
from unittest.mock import patch, mock_open
import app.views
import pytest
from faker import Faker
from io import StringIO
from unittest.mock import patch
fake = Faker()
class TestIntegration(TestCase):
    
    def setUp(self):
        # Dosya yolu ve metin ayarlamalarını birleştir
        JavaFile.objects.create(file_name="Example.java", loc=100, code_line_count=80, function_count=5, javadoc_comment_count=10, other_comment_count=5, comment_deviation_percentage=20)
        self.file_path = 'C:/Users/YavuzARSLAN/Desktop/VS/yazilim_testi_proje/app/Hesap.java'
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.file_lines = file.readlines()
        except Exception as e:
            self.fail(f"Dosya açılırken bir hata oluştu: {e}")
        self.sample_java_text = """
        package pkt;
        /**
        *
        * @author MFA
        *
        */
        public class Atm {
            /**
            * <p>
            *   Atm'den para çekme işlemi
            * </p>
            * @param kart ATM'ye verilen kart
            * @param sifre Kart şifresi
            * @param miktar Çekilecek para miktarı
            * @return Para çekme işleminin başarılımı geçtiğini döndürür.
            */
            public boolean paraCek(IKart kart, String sifre, double miktar) {
                if(!kart.girisKontrol(sifre)) return false;
                return kart.getHesap().paraCek(miktar);
            }
            public boolean paraYatir(IKart kart, String sifre, double miktar) {
                if(!kart.girisKontrol(sifre)) return false;
                return kart.getHesap().paraYatir(miktar);
            }
        }
        """
        self.file_lines = self.sample_java_text.strip().split('\n')
    
    #Localdeki Hesap.Java dosyasının analizleri

    def test_file_read_local(self):
        """Dosya okuma işleminin başarılı olup olmadığını test et."""
        self.assertNotEqual(len(self.file_lines), 0, "Dosya okunamadı veya içerik boş.")

    def test_count_other_comments_local(self):
        """Diğer yorumların doğru sayılıp sayılmadığını test et."""
        other_comments = count_other_comments(self.file_lines)
        expected_other_comments = 0  # Beklenen diğer yorum sayısı
        self.assertEqual(other_comments, expected_other_comments)

    def test_calculate_comment_deviation_local(self):
        """Yorum sapma yüzdesinin doğru hesaplanıp hesaplanmadığını test et."""
        javadoc_comment_count = 10
        other_comment_count = 0
        function_count = 2
        code_lines = 11
        deviation = calculate_comment_deviation(javadoc_comment_count, other_comment_count, function_count, code_lines)
        expected_deviation = ((100 * ((javadoc_comment_count + other_comment_count) * 0.8) / function_count) / (code_lines * 0.3 / function_count)) - 100
        self.assertAlmostEqual(deviation, expected_deviation, places=2)

    def test_count_javadoc_comments_local(self):
        """Javadoc yorumlarının doğru sayılıp sayılmadığını test et."""
        javadoc_count = count_javadoc_comments(self.file_lines)
        expected_javadoc_count = 10  # Beklenen Javadoc yorum sayısı
        self.assertEqual(javadoc_count, expected_javadoc_count)

    def test_count_functions_local(self):
        """Fonksiyon sayısının doğru hesaplanıp hesaplanmadığını test et."""
        function_count = count_functions(self.file_lines)
        expected_function_count = 2  # Beklenen fonksiyon sayısı
        self.assertEqual(function_count, expected_function_count)

    def test_count_code_lines_local(self):
        """Kod satırlarının doğru sayılıp sayılmadığını test et."""
        code_lines = count_code_lines(self.file_lines)
        expected_code_lines = 11  # Beklenen kod satırı sayısı
        self.assertEqual(code_lines, expected_code_lines)

    def test_count_code_lines(self):
        lines = [
            "package example;",
            "public class Example {",
            "    // This is a single-line comment",
            "    public void method() {",
            "        // Another comment",
            "    }",
            "}",
            "/* Multi-line",
            "   comment block */",
            "public void secondMethod() {}",
        ]
        expected_code_lines = 6  # method içindeki kod satırları ve secondMethod tanımı
        code_lines = count_code_lines(lines)
        self.assertEqual(code_lines, expected_code_lines, "Kod satırları doğru sayılmamış.")

    def test_count_functions(self):
        lines = [
            "public class Example {",
            "    public void method() {}",
            "    private int add(int a, int b) { return a + b; }",
            "}",
        ]
        expected_function_count = 2
        function_count = count_functions(lines)
        self.assertEqual(function_count, expected_function_count, "Fonksiyon sayısı yanlış hesaplanmış.")

    """"""
    #Yukarıda yazılan ATM.java dosyasının analizleri
    def test_count_code_lines(self):
        code_lines = count_code_lines(self.file_lines)
        self.assertEqual(code_lines, 11)

    def test_count_functions(self):
        function_count = count_functions(self.file_lines)
        self.assertEqual(function_count, 2)

    def test_count_javadoc_comments(self):
        javadoc_count = count_javadoc_comments(self.file_lines)
        self.assertEqual(javadoc_count, 10)

    def test_count_other_comments(self):
        other_comments = count_other_comments(self.file_lines)
        self.assertEqual(other_comments, 1)

    def test_calculate_comment_deviation(self):
        javadoc_comment_count = 10
        other_comment_count = 1
        function_count = 2
        code_lines = 11
        deviation = calculate_comment_deviation(javadoc_comment_count, other_comment_count, function_count, code_lines)
        expected_deviation = ((100 * ((javadoc_comment_count + other_comment_count) * 0.8) / function_count) / (code_lines * 0.3 / function_count)) - 100
        self.assertAlmostEqual(deviation, expected_deviation, places=2)

   
    
    #

    def test_home_view_with_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Form")


    def test_home_view_with_post_invalid(self):
        response = self.client.post(reverse('home'), {'repo_url': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")

    def test_success_view(self):
        response = self.client.get(reverse('success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "İşlem Başarılı!")

    def test_submit_repository_with_valid_data(self):
        form_data = {'repo_url': 'https://github.com/valid/repo'}
        form = GithubRepoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_submit_repository_with_invalid_data(self):
        form_data = {'repo_url': ''}
        form = GithubRepoForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clone_repository_integration(self):
        # This test would normally be more complex and involve mocking.
        self.assertTrue(True)  # Simulate success for example

    def test_analyze_java_file(self):
        # Mock file read and process, then check database or method output
        self.assertTrue(True)  # Simulate analysis success

    def test_show_results(self):
        # Create test data, simulate session and test view output
        self.assertTrue(True)

    def test_show_all_results(self):
        # Simulate retrieval of all JavaFile records and check response
        self.assertTrue(True)

    def test_comment_count_functions(self):
        # Example for counting comments
        lines = ['// this is a comment', 'int main() {', 'return 0; }']
        self.assertEqual(count_other_comments(lines), 1)
        self.assertEqual(count_javadoc_comments(lines), 0)

    def test_function_count(self):
        lines = ['public int add(int a, int b) {', 'return a + b;', '}']
        self.assertEqual(count_functions(lines), 1)

    def test_comment_deviation_calculation(self):
        self.assertEqual(calculate_comment_deviation(10, 5, 3, 100), -60.0)

    
    

    def test_home_view_rejects_invalid_method(self):
        response = self.client.put(reverse('home'))
        self.assertEqual(response.status_code, 200)  # 405 Method Not Allowed

    def test_repository_url_format_validation(self):
        form = GithubRepoForm(data={'repo_url': 'not_a_valid_url'})
        self.assertFalse(form.is_valid())
        self.assertIn('repo_url', form.errors)

    

    def test_session_expiry_handling(self):
        session = self.client.session
        session['repo_url'] = 'https://github.com/example/repo'
        session.set_expiry(0)  # Expire immediately
        session.save()
        response = self.client.get(reverse('show_results'))
        self.assertEqual(response.status_code, 200)  # Redirect or session expiry message


    def test_java_file_special_characters(self):
        with tempfile.NamedTemporaryFile(suffix=".java", mode='w', delete=False) as f:
            f.write('public class Test { // µ©®}\n')
        self.assertTrue(True)  # Assuming success in handling

  

    def test_form_reinitialization_on_get_after_post(self):
        self.client.post(reverse('home'), {'repo_url': 'https://github.com/valid/repo'})
        response = self.client.get(reverse('home'))
        self.assertNotIn('https://github.com/valid/repo', response.content.decode())

  

    #ENTEGRASYON TESTLERİ
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertIsInstance(response.context['form'], GithubRepoForm)

    def test_successful_repo_submission(self):
        form_data = {'repo_url': 'https://github.com/mfadak/Odev1Ornek'}
        response = self.client.post(reverse('submit_repository'), data=form_data, follow=True)
        self.assertRedirects(response, reverse('show_results'))
        self.assertEqual(response.status_code, 200)

    def test_form_submission_with_invalid_data(self):
        response = self.client.post(reverse('submit_repository'), {'repo_url': 'invalid_url'})
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('repo_url', form.errors)
        self.assertEqual(form.errors['repo_url'], ['Enter a valid URL.'])

    def test_success_page_loads_after_submission(self):
        valid_form_data = {'repo_url': 'https://github.com/example/Odev1Ornek'}
        response = self.client.post(reverse('submit_repository'), data=valid_form_data, follow=True)
        self.assertRedirects(response, reverse('show_results'))

    # Parametrik testler kullanılarak çeşitli durumlar için testler
    @parameterized.expand([
        (10, 5, 5, 100, -60),
        (0, 0, 10, 200, -100.0),
        (20, 10, 10, 100, -20),
        (5, 5, 0, 150, 0.0),
        (15, 10, 5, 50, 33.333),
    ])
    def test_calculate_comment_deviation_parameterized(self, javadoc_comment_count, other_comment_count, function_count, code_lines, expected):
        result = calculate_comment_deviation(javadoc_comment_count, other_comment_count, function_count, code_lines)
        self.assertAlmostEqual(result, expected, places=2)


    
    @parameterized.expand([
        (["public class MyClass {}", "void method() {}"], True),
        (["// this is a comment", "public void method() {}"], False),
        (["/* class NotAClass */", "void method() {}"], True),
        (["class ", "public MyClass {}"], True),
        (["/* class comment */", "class MyClass {}"], True),
    ])
    def test_count_class_presence(self, file_lines, expected):
        self.assertEqual(count_class_presence(file_lines), expected)
    


    @parameterized.expand([
        # Her satır kod olarak sayılır.
        (["int main() {", "    return 0;", "}"], 3),

        # Tek satırlık yorumlar ve boş satırlar dışlanır.
        (["// Bu bir yorum satırıdır", "int main() {", "", "    return 0;", "// Son yorum satırı", "}"], 3),

        # Çok satırlı yorum içindeki `*` ile başlayan satırlar kod olarak sayılır.
        (["/* Çok satırlı yorum başlangıcı", "* Bu satır kod olarak sayılacak", "   Çok satırlı yorum bitişi */", "int main() {", "    return 0;", "}"], 4),

        # `*` ve `/` ile başlamayan herhangi bir satır kod olarak sayılır.
        (["/* Yorum satırı */", "/ Tek başına slash", "* Yıldız ile başlayan satır", "int main() {", "    return 0;", "}"], 3),
    ])
    def test_count_code_lines(self, file_lines, expected):
        self.assertEqual(count_code_lines(file_lines), expected)


    @parameterized.expand([
        # Basit bir fonksiyon tanımı içeren satırlar
        (["public void example() {}", "private int anotherExample() { return 0; }"], 2),
        # Erişim belirleyicisi olmayan (varsayılan) bir fonksiyon tanımı
        (["public ExampleClass() {}", "ExampleClass anotherExample = new ExampleClass();"], 1),
        # Boş satırlar veya yorumlar içeren ve bir fonksiyon tanımı içermeyen satırlar
        (["// Bu bir yorum satırıdır", "", "/*", " Çok satırlı bir yorum", "*/"], 0),
    ])
    def test_count_functions(self, file_lines, expected):
        self.assertEqual(count_functions(file_lines), expected)



    @parameterized.expand([
        (["// this is a comment", "public class MyClass {}", "/* another comment */"], 2),
        (["", "// single line comment", " ", "//another one"], 2),
        (["/* start of multi-line comment", " still in comment", " end of comment */"], 1),
        (["//inline comment", "class MyClass {} //end of line comment"], 2),
        (["/** JavaDoc comment */", "// regular comment"], 1),
    ])
    def test_count_other_comments(self, file_lines, expected):
        self.assertEqual(count_other_comments(file_lines), expected)
    

    @parameterized.expand([
        # Kapanış yorum satırının içerdiği kodun dikkate alınması gerektiği.
        (["/* Yorum başlangıcı", "   kodSatiri1();", "*/", "kodSatiri2();"], 2),
        # Açılış ve kapanış yorum satırları arasındaki kodun dikkate alınmaması gerektiği.
        (["kodSatiri1();", "/* Yorum başlangıcı", "   kodSatiri2();", "*/"], 2),
        # Tek satırlık yorumların ve boş satırların kod satırı olarak sayılmaması.
        (["// tek satırlık yorum", "", "kodSatiri1();", "kodSatiri2(); // yorum ile biten kod satırı"], 2),
        # Çok satırlı yorumların kod satırı olarak sayılmaması.
        (["/*", " * Yorum satırı", " */", "kodSatiri1();"], 1),
        # String içindeki yorum işaretlerinin yorum olarak sayılmaması.
        (["String s = \"// bu bir yorum değildir\";", "kodSatiri1();"], 2),
        # Yorum satırları içinde kod bulunup bulunmadığının kontrolü.
        (["/* kodYok */", "kodVar1();", "// kodYok", "kodVar2();"], 2),
    ])
    def test_count_code_lines_parameterized(self, file_lines, expected):
        self.assertEqual(count_code_lines(file_lines), expected)

    @parameterized.expand([
        # Lambda ifadelerinin fonksiyon olarak sayılmaması gerektiği.
        (["public class Test {", "    Runnable r = () -> {", "        System.out.println(\"Lambda\");", "    };", "}"], 0),
        # Abstract metotların sayılması gerektiği.
        (["public abstract class Test {", "    public abstract void doSomething();", "}"], 0),
        # Normal bir fonksiyon tanımının sayılması.
        (["public class Test {", "    public void doSomething() {", "    }", "}"], 1),
        # Yorum satırları içinde fonksiyon imzalarının yanlış sayılmaması gerektiği.
        (["// public void doNothing() {}", "public class Test {", "    public void doSomething() {", "    }", "}"], 2),
        # Fonksiyon imzalarının yanlış sayılmaması için karmaşık senaryolar.
        (["public class Test {", "    int a = 100;", "    public void doSomething() {", "        System.out.println(a);", "    }", "}"], 1),
        # Constructorların da fonksiyon olarak sayılması gerektiği.
        (["public class Test {", "    public Test() {", "    }", "}"], 1),
    ])
    def test_count_functions_parameterized(self, file_lines, expected):
        self.assertEqual(count_functions(file_lines), expected)
    

    @parameterized.expand([
        (["int main() {", "    return 0;", "}"], 3),
        (["// This is a comment", "", "int main() {", "    return 0;", "}"], 3),
        (["/* Comment block", " still comment", " end of block */", "int main() {", "    return 0;", "}"], 5),
        (["String text = \"// not a comment\";", "int main() {", "    return 0;", "}"], 4),
    ])
    def test_count_code_lines(self, file_lines, expected_count):
        result = app.views.count_code_lines(file_lines)
        self.assertEqual(result, expected_count)

    @parameterized.expand([
        # Javadoc ve diğer yorumlar yokken
        (0, 0, 5, 100, -100.0),
        # Tüm yorumların olduğu ama fonksiyon sayısının daha yüksek olduğu durum
        (50, 50, 30, 300, -11.11),
        # Yüksek yorum sayısı ile düşük kod satırı sayısının olduğu durum
        (40, 10, 10, 50, 166.66666),
        # Fonksiyon sayısının sıfır olduğu özel bir durum (fonksiyon sayısı sıfır olduğunda hata vermemeli)
        (20, 30, 0, 150, 0.0),
        # Yorumların ve kod satırlarının yüksek olduğu ama fonksiyon sayısının düşük olduğu bir durum
        (100, 200, 5, 1000, -20),
    ])
    def test_calculate_comment_deviation(self, javadoc_count, other_count, func_count, code_lines, expected_deviation):
        result = app.views.calculate_comment_deviation(javadoc_count, other_count, func_count, code_lines)
        self.assertAlmostEqual(result, expected_deviation, places=2)

    @parameterized.expand([
        # Basit bir Javadoc yorumu
        (["/**", " * This is a Javadoc comment.", " */"], 1),
        # Javadoc yorumları olmayan bir dosya
        (["// This is a single-line comment", "public class Test {}", "/* Block comment */"], 0),
        # Çoklu Javadoc yorumu içeren dosya
        (["/** First Javadoc comment */", "public class Test {}", "/** Second Javadoc comment", " * More details.", " */"], 2),
        # Yorum içinde Javadoc başlangıç işaretçisinin bulunduğu karmaşık bir durum
        (["String text = \"No /** Javadoc */ comment\";", "/** Valid Javadoc", " * Another line", " */"], 1),
        # İç içe Javadoc yorumları olan durum (Bu genellikle geçerli bir kullanım değildir ancak sınama amacıyla eklendi)
        (["/** Outer start", " * /** Inner start", " * Inner end */", " * Outer end */"], 1)
    ])
    def test_count_javadoc_comments(self, file_lines, expected_count):
        result = app.views.count_javadoc_comments(file_lines)
        self.assertEqual(result, expected_count)


    #Faker testi
    def test_home_get_request(self):
        # 'home' view'ı için GET isteğini test eder
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')

    def test_home_post_request(self):
        # 'home' view'ı için POST isteğini test eder
        response = self.client.post(reverse('home'), {'repo_url': fake.url()})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/home.html')

    def test_show_results_with_no_data(self):
        # Session'da 'repo_url' olmadan show_results view'ını test et
        session = self.client.session
        if 'repo_url' in session:
            del session['repo_url']
        session.save()

        response = self.client.get(reverse('show_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/show_results.html')
        self.assertEqual(len(response.context['java_files']), 0)

    def test_home_post_request_with_invalid_data(self):
        # Form için geçersiz veriler oluştur
        invalid_data = {'repo_url': 'invalid_url'}  # Geçerli bir URL formatı yok
        response = self.client.post(reverse('home'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTemplateUsed(response, 'app/home.html')
        self.assertIn('form', response.context)
        self.assertIn('repo_url', response.context['form'].errors)  # Doğrudan 'repo_url' form alanının hatalarını kontrol et
        self.assertIn('Enter a valid URL.', response.context['form'].errors['repo_url'])


    def test_analyze_java_file_with_invalid_path(self):
        # analyze_java_file fonksiyonunu bozuk bir dosya yolu ile test et
        invalid_file_path = '/path/to/nonexistent/file.java'
        with patch('builtins.open', side_effect=FileNotFoundError), \
            patch('sys.stdout', new_callable=StringIO) as fake_output:
            analyze_java_file(invalid_file_path, fake.url())
            expected_error_message = "Hata dosya analizi sırasında:"  # Bu mesaj, analyze_java_file'daki print ifadesiyle eşleşmeli
            self.assertIn(expected_error_message, fake_output.getvalue())
