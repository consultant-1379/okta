FROM centos/python-36-centos7 
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
USER root

RUN yum -y install ca-certificates
COPY EGADRootCA.crt /etc/pki/ca-trust/source/anchors/EGADRootCA.crt
RUN update-ca-trust
ENV REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt
RUN yum -y install python3-devel && \ 
    yum -y install openldap-devel
COPY . /code/
