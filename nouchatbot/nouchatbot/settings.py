"""
Django settings for nouchatbot project.

Generated by 'django-admin startproject' using Django 2.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
#https://noutest.herokuapp.com/callback

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'c)q8cbe8ebp=p-3r@so9=$c6j-s8+t7@_dcx8sfdog5ta_!i2i'
#LINE_CHANNEL_ACCESS_TOKEN = 'Ay2z7UYdla8stybYoxq20bGBWh89Y+c6/+OkpneCbhXOeR+Yr+alkpLpfjfUUdzk7f6LmKHL0MUUk2R+saG/DN/UY2xTMIpG8YAJnDfIucg7Sy3hGKFcjyXfQ3estm8lBs29NCpMx7XMimtTvaH+BwdB04t89/1O/w1cDnyilFU='
#LINE_CHANNEL_SECRET = '41eb59aa296c9f38603de5bfcfa94692'

#for Testing
SECRET_KEY = 'Uf7c156f240de13f6e47856b4b1578d9f'
LINE_CHANNEL_ACCESS_TOKEN = 'Ay2z7UYdla8stybYoxq20bGBWh89Y+c6/+OkpneCbhXOeR+Yr+alkpLpfjfUUdzk7f6LmKHL0MUUk2R+saG/DN/UY2xTMIpG8YAJnDfIucg7Sy3hGKFcjyXfQ3estm8lBs29NCpMx7XMimtTvaH+BwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '41eb59aa296c9f38603de5bfcfa94692'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'botapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nouchatbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')], # 加上templates路徑
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nouchatbot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    #'mypostreSQL':{   #配置第二個資料庫節點名稱->PostreSQL on HeroKu
    #    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #    'NAME': 'dbnk1cg6na4487',
    #    'USER': 'bgaxopexrmbktp',
    #    'PASSWORD': 'e0f8e6a3989126ea9a783223c0acef00354dde1c775f9d11e85f1ec19873cadd',
    #    'HOST':'ec2-3-233-7-12.compute-1.amazonaws.com',
    #    'PORT':'5432',   
    #},
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [  #加入 static 路徑
	os.path.join(BASE_DIR, 'static'),
]


