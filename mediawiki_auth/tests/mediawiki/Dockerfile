FROM wikimedia/mediawiki
RUN mkdir /conf
COPY CustomSettings.php /conf/
EXPOSE 80 443
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apachectl", "-e", "info", "-D", "FOREGROUND"]
