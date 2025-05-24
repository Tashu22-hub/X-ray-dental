FROM node:18
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]


// Update this URL in fetch:
const res = await fetch("http://localhost:8000/upload-dicom/")
