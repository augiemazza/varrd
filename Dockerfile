FROM node:20-slim
RUN npm install -g mcp-proxy@6.4.3
CMD ["mcp-proxy", "https://app.varrd.com/mcp"]
