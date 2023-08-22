FROM python:3.6-slim-buster

# OS libraries
RUN apt-get update
RUN apt-get install -y libappindicator1 \
fonts-liberation \
wget \
unzip \
dpkg \
libcurl3-gnutls \
libcurl3-nss \
libcurl4 \
libdrm2 \
libgbm1 \
libgtk-3-0 \
libnspr4 \
libnss3 \
libu2f-udev \
libvulkan1 \
libxkbcommon0 \
xdg-utils \
libasound2

RUN apt-get -y clean all

# Install chrome driver and browser
WORKDIR /bin

RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome*.deb

RUN chmod 755 /bin/chromedriver

# Install requirements
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY code/ .

CMD ["python3", "update_database.py"]


