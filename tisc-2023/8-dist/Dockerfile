FROM node:14
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY server.js views/ db.js ./
EXPOSE 3000

COPY .aws/ /root/.aws/
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

CMD bash -c '/usr/local/bin/wait-for-it.sh -t 60 mysql:3306 -- node server.js'
