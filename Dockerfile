FROM node:20-slim
RUN npm install -g mcp-remote
CMD ["mcp-remote", "https://app.varrd.com/mcp"]
