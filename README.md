## Тестовое LestaGames

Веб-приложение для анализа текстовых файлов
 - Текстовые файлы загружаются в формате _.txt_
 - Содержимое автоматически обрабатывается
 - Выводится таблица с топ-50 словами, упорядоченными по убывания _idf_

---

 #### Примечание:
 - При каждом запуске приложения база данных обнуляется. То есть статистика из предыдущих сессий не сохраняется
 - Для информативного _idf_ рекомендуется загрузить хотя бы несколько файлов
 - В папке _tests/files/_ есть несколько файлов для тестового прогона

---

#### Установка и запуск:
```bash
git clone https://github.com/gedfalk/lestaGames.git
cd lestaGames

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

fastapi run
```

