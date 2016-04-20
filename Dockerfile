FROM centos/httpd
RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
RUN yum -y install mod_wsgi openjpeg-devel libjpeg-turbo-devel zlib-devel make glibc-devel gcc patch postgresql postgresql-devel python-pip python-devel python-memcached && yum clean all
RUN pip install psycopg2
RUN mkdir -p /var/askbot-site
COPY . /askbot-devel
RUN rm -rf /askbot-devel/.git
RUN cd /askbot-devel && python setup.py install
RUN askbot-setup --dir-name=/var/askbot-site --db-engine=1 --db-name=askbotdb --db-user=askbotuser --db-password=encrypted-db-password --domain=askbot.salecycle.com
RUN cd /var/askbot-site && yes "yes" | python manage.py collectstatic
RUN ln -s /var/askbot-site/askbot /var/askbot-site/application
RUN mkdir /usr/share/httpd/.python-eggs && chown apache /usr/share/httpd/.python-eggs && chown apache /var/askbot-site/askbot/upfiles
COPY deploy/httpd.conf /etc/httpd/conf/httpd.conf
COPY deploy/settings.py /var/askbot-site/
CMD ["/run-httpd.sh"]
