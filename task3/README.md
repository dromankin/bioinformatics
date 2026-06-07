# Ссылка на прочтения

https://www.ncbi.nlm.nih.gov/sra/?term=ERR15404843


# Референсный геном - e.coli
https://www.ncbi.nlm.nih.gov/assembly/GCF_000005845.2/ 

# Скрипты

**pipeline.sh** - основной пайплайн на bash

**script.py** - скрипт по парсингу flagstat

**pipeline_hello.py** - тестовый пайплайн на Toil

**pipeline.py** - основной пайплайн на Toil

# Логи
Соответствующие файлы расширения **.log**


# Фреймворк (Toil)

## Установка
```bash
pip install --user virtualenv
python3 -m virtualenv ~/venv
source ~/venv/bin/activate
pip install toil
```

## Запуск пайплайна

```bash
python3 pipeline.py file:my-job-storage
```

**Примечание**

Все побочные файлы (.fna, .fastq) должны быть в одной директории с файлом Toil-пайплайна

# Визуализация

C помощью **graphviz**

Отличия: параллелятся индексация и запуск fastq, в целом более упрощенная схема