from tkinter import *
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext
from tkinter.filedialog import askopenfilename

import pymorphy2
from nltk.tokenize import word_tokenize, sent_tokenize
import bs4 as BeautifulSoup
import urllib.request
import io  # для декодировки utf-8 из txt файла
import re
import validators


# def start_window1():
#     new_window_1 = Toplevel(window)
#     new_window_1.title('Окно 1')
#     new_window_1.geometry('600x400')
#     lbl = Label(window, text="Привет", font=("Arial Bold", 20)).pack()


def main_window():
    destroy_widgets()
    choice = IntVar()
    Label(window, text="Оберіть шлях вводу даних", font="Solasta 30").pack()
    Button(window, width=25, height=5, text="Посилання на вікіпедію", font="Solasta 20", relief=RIDGE, bd=3,
           command=lambda: b_url_presed(choice.get())).pack()
    Button(window, width=25, height=5, text="Пряме введення тексту", font="Solasta 20", relief=RIDGE, bd=3,
           command=lambda: b_raw_presed(choice.get())).pack()
    Button(window, width=25, height=5, text="Введення тексту з файлу", font="Solasta 20", relief=RIDGE, bd=3,
           command=lambda: b_txt_presed(choice.get())).pack()

    bottomframe = Frame(window)
    Label(bottomframe, text="Мова тексту", font="Solasta 20").pack()
    Radiobutton(bottomframe, text="ukr", font="Solasta 25", variable=choice, indicatoron=0, value=1).pack(side=LEFT)
    Radiobutton(bottomframe, text="rus", font="Solasta 25", variable=choice, indicatoron=0, value=0).pack(side=LEFT)
    bottomframe.pack(side=BOTTOM, anchor=W)


def destroy_widgets():
    for widget in window.winfo_children():
        widget.destroy()


def b_url_presed(lang):
    destroy_widgets()
    Label(window, text="Введіть посилання на сторінку вікіпедії", font="Solasta 30").pack()
    html_url = Entry(window, width="200", font="Solasta 15")
    html_url.pack(pady=20)
    Button(window, width=25, height=5, text="Продовжити", font="Solasta 15", relief=RIDGE, bd=3,
           command=lambda: get_url(html_url.get(), lang)).pack()
    Button(window, width=25, height=5, text="Назад", font="Solasta 15", relief=RIDGE, bd=3,
           command=main_window).pack()
    Button(window, width=25, height=5, text="Вийти", font="Solasta 15", relief=RIDGE, bd=3,
           command=on_closing).pack()


def b_txt_presed(lang):
    destroy_widgets()
    Label(window, text="Виберіть файл для обробки", font="Solasta 30").pack()
    try:
        filename = askopenfilename(filetypes=(("txt files", "*.txt"), ("word files", "*.doc")))
        # show an "Open" dialog box and return the path to the selected file
        with open(filename, "r") as f:
            text = f.read()
            Button(window, width=25, height=5, text="Продовжити", font="Solasta 15", relief=RIDGE, bd=3,
                   command=lambda: pre_result(text, lang)).pack()
            Button(window, width=25, height=5, text="Назад", font="Solasta 15", relief=RIDGE, bd=3,
                   command=main_window).pack()
            Button(window, width=25, height=5, text="Вийти", font="Solasta 15", relief=RIDGE, bd=3,
                   command=on_closing).pack()
    except FileNotFoundError:
        main_window()
        messagebox.showwarning(title="Помилка", message="Ви не правильно вибрали файл.")


def b_raw_presed(lang):
    destroy_widgets()
    Label(window, text="Введіть текст для обробки", font="Solasta 30").pack()
    result_text = scrolledtext.ScrolledText(window, undo=True, wrap=WORD)
    result_text['font'] = ('consolas', '12')
    result_text.pack(expand=True, fill='both')
    bottomframe = Frame(window)
    bottomframe.pack(side=BOTTOM, pady=10)
    Button(bottomframe, width=25, height=5, text="Назад", font="Solasta 15", relief=RIDGE, bd=3,
           command=main_window).pack(side=LEFT)
    Button(bottomframe, width=25, height=5, text="Вийти", font="Solasta 15", relief=RIDGE, bd=3,
           command=on_closing).pack(side=LEFT)
    Button(bottomframe, width=25, height=5, text="Продовжити", font="Solasta 15", relief=RIDGE, bd=3,
           command=lambda: pre_result(result_text.get("1.0", END), lang)).pack(side=LEFT)


def pre_result(text, lang):
    if len(text) < 500:
        messagebox.showwarning(title="Помилка", message="Ви вибрали файл c недостатньою кількостю речень.")
        main_window()
    else:
        result(text, lang)


def parse_url(url):
    fetched_data = urllib.request.urlopen(url)

    article_read = fetched_data.read()

    # parsing the URL content and storing in a variable
    article_parsed = BeautifulSoup.BeautifulSoup(article_read, 'html.parser')

    # returning <p> tags
    paragraphs = article_parsed.find_all('p')

    article_content = ''

    # looping through the paragraphs and adding them to the variable
    for p in paragraphs:
        article_content += p.text

    return article_content


def get_url(url, lang):
    validators.url(url)
    if validators.url(url) and "wikipedia.org" in url:
        result(parse_url(url), lang)
    else:
        messagebox.showwarning(title="Помилка", message="Ви не правильно ввели посилання.")
        main_window()


def create_dictionary_table(text_string, lang, morph) -> dict:
    # removing stop words

    stop_words = set(line.strip() for line in io.open(lang, mode="r", encoding="utf-8"))
    words = word_tokenize(text_string)

    # reducing words to their root form
    # stem = PorterStemmer()  # Инициализация объекта типа <PorterStemmer>

    # creating dictionary for the word frequency table
    frequency_table = dict()

    for wd in words:
        wd = morph.parse(wd)[0].normal_form  # Преобразование слова в корневую форму ( только англ ).
        if wd in stop_words:
            continue
        if wd in frequency_table:
            frequency_table[wd] += 1
        else:
            frequency_table[wd] = 1

    return frequency_table


def calculate_sentence_scores(sentences, frequency_table, morph) -> dict:
    # algorithm for scoring a sentence by its words
    sentence_weight = dict()

    for sentence in sentences:
        # sentence_wordcount = (len(word_tokenize(sentence)))
        sentence_wordcount_without_stop_words = 0
        sentence_in_work = "".join(
            c for c in sentence if c.isalpha() or c == " ")  # добавляем в строку всё буквы и пробелы
        sentence_in_work = re.sub(" +", " ", sentence_in_work)
        sentence_in_work = sentence_in_work.split(" ")
        processed_sentence = ""
        for elem in sentence_in_work:
            processed_sentence += morph.parse(elem)[0].normal_form + " "
        processed_sentence = processed_sentence[:-1]
        for word_weight in frequency_table:
            if word_weight in processed_sentence.lower():
                sentence_wordcount_without_stop_words += 1
                if sentence[:7] in sentence_weight:
                    sentence_weight[sentence[:7]] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:7]] = frequency_table[word_weight]

        try:
            sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]] / sentence_wordcount_without_stop_words
        except KeyError:
            continue

    # [:7] Просто для укорачивания предложения при его записи в sentence_weight (что-бы не писать предложение полностью)
    # sentence_weight[sentence[:7]] / sentence_wordcount_without_stop_words ( нужно для того, что-бы длинные предложение
    # не имели преимуществ перед короткими т.е делит на кол-во слов в предложении ( без стоп слов ) )

    return sentence_weight


def calculate_average_score(sentence_weight) -> float:
    # calculating the average score for the sentences
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]

    # getting sentence average value from source text
    average_score = (sum_values / len(sentence_weight))

    return average_score


def get_article_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    article_summary = ''

    for sentence in sentences:
        if sentence[:7] in sentence_weight and sentence_weight[sentence[:7]] >= (threshold):
            article_summary += " " + sentence
            sentence_counter += 1

    return [article_summary, sentence_counter]


def run_article_summary(article, lang, morph):
    # creating a dictionary for the word frequency table
    frequency_table = create_dictionary_table(article, lang, morph)

    # tokenizing the sentences
    sentences = sent_tokenize(article)

    # algorithm for scoring a sentence by its words
    sentence_scores = calculate_sentence_scores(sentences, frequency_table, morph)

    # getting the threshold
    threshold = calculate_average_score(sentence_scores)

    # producing the summary
    article_summary = get_article_summary(sentences, sentence_scores, 1.2 * threshold)  # 1 коеф.

    return [article_summary, len(sentences)]


def result(text, lang):
    destroy_widgets()

    if lang:
        lang = "resources/ukrainian.txt"
        morph = pymorphy2.MorphAnalyzer(lang='uk')
    else:
        lang = "resources/russian.txt"
        morph = pymorphy2.MorphAnalyzer()

    summary_results = run_article_summary(text, lang, morph)

    # print(
    #     f"Початкова кількість речень: {summary_results[1]} --> Кількість речень після виділення основної суті: {summary_results[0][1]}")
    # print(re.sub("\n", " ", summary_results[0][0]).strip())

    result_text = scrolledtext.ScrolledText(window, undo=True, wrap=WORD)
    result_text['font'] = ('consolas', '12')
    result_text.pack(expand=True, fill='both')
    output = f"Початкова кількість речень: {summary_results[1]} --> Кількість речень після виділення основної суті: {summary_results[0][1]}" + "\n\n"
    output += re.sub("\n", " ", summary_results[0][0]).strip()

    result_text.insert(1.0, output)
    result_text.configure(state='disabled')

    bottomframe = Frame(window)
    bottomframe.pack(side=BOTTOM, pady=10)
    Button(bottomframe, width=25, height=5, text="Повернутися до початку", font="Solasta 15", relief=RIDGE, bd=3,
           command=main_window).pack(side=LEFT, padx=10)
    Button(bottomframe, width=25, height=5, text="Зберегти результат в файл", font="Solasta 15", relief=RIDGE, bd=3,
           command=lambda: save(output)).pack(side=LEFT, padx=10)
    Button(bottomframe, width=25, height=5, text="Показати початковий текст", font="Solasta 15", relief=RIDGE, bd=3,
           command=lambda: show_sub_window(text)).pack(side=LEFT, padx=10)
    Button(bottomframe, width=25, height=5, text="Вийти", font="Solasta 15", relief=RIDGE, bd=3,
           command=on_closing).pack(side=LEFT, padx=10)


def show_sub_window(text):
    sub_window = Toplevel(window)
    sub_window.title('Original text')
    sub_window.geometry('600x800')

    result_text = scrolledtext.ScrolledText(sub_window, undo=True, wrap=WORD)
    result_text['font'] = ('consolas', '12')
    result_text.pack(expand=True, fill='both')

    result_text.insert(1.0, text)
    result_text.configure(state='disabled')


def save(output):
    with open('result.doc', 'w', encoding="utf-8") as f:
        f.write(output)
    messagebox.showinfo(title="Збереження файлу", message="Файл збережено.")


def on_closing():
    if messagebox.askokcancel("Вихід з програми", "Ви бажаєте вийти з програми?"):
        window.destroy()


window = Tk()
window.protocol('WM_DELETE_WINDOW', on_closing)
window.title('Text summarization')
window.geometry('1280x720')
window.resizable(False, False)
main_window()
window.mainloop()
