FROM apify/actor-node-playwright-chrome:22

USER root
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY --chown=myuser:myuser . .

RUN mkdir -p /app/storage && chown myuser:myuser /app/storage
USER myuser

EXPOSE 3000
CMD ["npm", "start"]
