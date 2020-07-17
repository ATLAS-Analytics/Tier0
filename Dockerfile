FROM atlasanalyticsservice/analytics-ingress-base:latest

LABEL maintainer Ilija Vukotic <ivukotic@cern.ch>

WORKDIR /home/analyticssvc

COPY *.py /home/analyticssvc/
COPY run.sh /

CMD [ "sleep","9999999" ]