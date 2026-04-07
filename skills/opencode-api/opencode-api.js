/**
 * opencode-api.js - opencode REST API JavaScript 客户端
 * 
 * 用法:
 * const client = new OpenCodeAPI({
 *   baseURL: process.env.OPENCODE_SERVER_BASE_URL || 'http://127.0.0.1:4096',
 *   username: process.env.OPENCODE_SERVER_USERNAME || 'opencode',
 *   password: process.env.OPENCODE_SERVER_PASSWORD // 可选
 * });
 */

class OpenCodeAPI {
  constructor(options = {}) {
    this.baseURL = options.baseURL || process.env.OPENCODE_SERVER_BASE_URL || 'http://127.0.0.1:4096';
    this.username = options.username || process.env.OPENCODE_SERVER_USERNAME || 'opencode';
    this.password = options.password || process.env.OPENCODE_SERVER_PASSWORD || '';
    this.authHeader = this.password 
      ? 'Basic ' + Buffer.from(`${this.username}:${this.password}`).toString('base64')
      : null;
  }

  async request(method, path, body = null) {
    const url = `${this.baseURL}${path}`;
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.authHeader) {
      headers['Authorization'] = this.authHeader;
    }

    const options = {
      method,
      headers,
    };

    if (body && (method === 'POST' || method === 'PATCH' || method === 'PUT')) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error ${response.status}: ${error}`);
    }

    // 处理空响应
    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  // ========== 全局端点 ==========
  
  async health() {
    return this.request('GET', '/global/health');
  }

  async getGlobalConfig() {
    return this.request('GET', '/global/config');
  }

  async updateGlobalConfig(config) {
    return this.request('PATCH', '/global/config', config);
  }

  async dispose() {
    return this.request('POST', '/global/dispose');
  }

  // ========== 会话管理 ==========
  
  async listSessions() {
    return this.request('GET', '/session');
  }

  async createSession(options = {}) {
    const { parentID, title, directory, workspace } = options;
    const body = {};
    if (parentID) body.parentID = parentID;
    if (title) body.title = title;
    return this.request('POST', '/session', body);
  }

  async getSession(sessionID) {
    return this.request('GET', `/session/${sessionID}`);
  }

  async deleteSession(sessionID) {
    return this.request('DELETE', `/session/${sessionID}`);
  }

  async updateSession(sessionID, updates) {
    return this.request('PATCH', `/session/${sessionID}`, updates);
  }

  async abortSession(sessionID) {
    return this.request('POST', `/session/${sessionID}/abort`);
  }

  async forkSession(sessionID, messageID = null) {
    const body = messageID ? { messageID } : {};
    return this.request('POST', `/session/${sessionID}/fork`, body);
  }

  async summarizeSession(sessionID, options) {
    return this.request('POST', `/session/${sessionID}/summarize`, options);
  }

  async shareSession(sessionID) {
    return this.request('POST', `/session/${sessionID}/share`);
  }

  async unshareSession(sessionID) {
    return this.request('DELETE', `/session/${sessionID}/share`);
  }

  async getSessionDiff(sessionID, messageID = null) {
    const path = messageID 
      ? `/session/${sessionID}/diff?messageID=${messageID}`
      : `/session/${sessionID}/diff`;
    return this.request('GET', path);
  }

  async getSessionTodo(sessionID) {
    return this.request('GET', `/session/${sessionID}/todo`);
  }

  async getSessionChildren(sessionID) {
    return this.request('GET', `/session/${sessionID}/children`);
  }

  async getSessionStatus() {
    return this.request('GET', '/session/status');
  }

  // ========== 消息 ==========
  
  async listMessages(sessionID, options = {}) {
    const { limit, before } = options;
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit);
    if (before) params.append('before', before);
    const query = params.toString() ? `?${params}` : '';
    return this.request('GET', `/session/${sessionID}/message${query}`);
  }

  async getMessage(sessionID, messageID) {
    return this.request('GET', `/session/${sessionID}/message/${messageID}`);
  }

  async sendMessage(sessionID, options) {
    const {
      messageID,
      model,
      agent,
      noReply,
      system,
      variant,
      parts,
      format,
    } = options;

    const body = { parts };
    if (messageID) body.messageID = messageID;
    if (model) body.model = model;
    if (agent) body.agent = agent;
    if (noReply !== undefined) body.noReply = noReply;
    if (system) body.system = system;
    if (variant) body.variant = variant;
    if (format) body.format = format;

    return this.request('POST', `/session/${sessionID}/message`, body);
  }

  async sendPromptAsync(sessionID, options) {
    // 异步发送，不等待响应
    const body = { ...options };
    return this.request('POST', `/session/${sessionID}/prompt_async`, body);
  }

  async deleteMessage(sessionID, messageID) {
    return this.request('DELETE', `/session/${sessionID}/message/${messageID}`);
  }

  async revertMessage(sessionID, messageID, partID = null) {
    const body = partID ? { messageID, partID } : { messageID };
    return this.request('POST', `/session/${sessionID}/revert`, body);
  }

  async unrevertMessages(sessionID) {
    return this.request('POST', `/session/${sessionID}/unrevert`);
  }

  // ========== 命令 ==========
  
  async executeCommand(sessionID, options) {
    const { command, arguments: args, agent, model, messageID } = options;
    const body = { command, arguments: args };
    if (agent) body.agent = agent;
    if (model) body.model = model;
    if (messageID) body.messageID = messageID;
    return this.request('POST', `/session/${sessionID}/command`, body);
  }

  async runShell(sessionID, options) {
    const { command, agent, model } = options;
    const body = { command, agent };
    if (model) body.model = model;
    return this.request('POST', `/session/${sessionID}/shell`, body);
  }

  // ========== 项目 ==========
  
  async listProjects(options = {}) {
    const { directory, workspace } = options;
    const params = new URLSearchParams();
    if (directory) params.append('directory', directory);
    if (workspace) params.append('workspace', workspace);
    const query = params.toString() ? `?${params}` : '';
    return this.request('GET', `/project${query}`);
  }

  async getCurrentProject(options = {}) {
    const { directory, workspace } = options;
    const params = new URLSearchParams();
    if (directory) params.append('directory', directory);
    if (workspace) params.append('workspace', workspace);
    const query = params.toString() ? `?${params}` : '';
    return this.request('GET', `/project/current${query}`);
  }

  async initGit(options = {}) {
    const { directory, workspace } = options;
    const params = new URLSearchParams();
    if (directory) params.append('directory', directory);
    if (workspace) params.append('workspace', workspace);
    const query = params.toString() ? `?${params}` : '';
    return this.request('POST', `/project/git/init${query}`);
  }

  async updateProject(projectID, updates) {
    return this.request('PATCH', `/project/${projectID}`, updates);
  }

  // ========== 文件 ==========
  
  async listFiles(path = '.', options = {}) {
    const { directory, workspace } = options;
    const params = new URLSearchParams({ path });
    if (directory) params.append('directory', directory);
    if (workspace) params.append('workspace', workspace);
    return this.request('GET', `/file?${params}`);
  }

  async readFile(path, options = {}) {
    const { directory, workspace } = options;
    const params = new URLSearchParams({ path });
    if (directory) params.append('directory', directory);
    if (workspace) params.append('workspace', workspace);
    return this.request('GET', `/file/content?${params}`);
  }

  async getFileStatus() {
    return this.request('GET', '/file/status');
  }

  // ========== 搜索 ==========
  
  async searchText(pattern, options = {}) {
    const { directory, workspace } = options;
    const params = new URLSearchParams({ pattern });
    if (directory) params.append('directory', directory);
    if (workspace) params.append('workspace', workspace);
    return this.request('GET', `/find?${params}`);
  }

  async findFiles(query, options = {}) {
    const { type, directory, limit, dirs } = options;
    const params = new URLSearchParams({ query });
    if (type) params.append('type', type);
    if (directory) params.append('directory', directory);
    if (limit) params.append('limit', limit);
    if (dirs !== undefined) params.append('dirs', String(dirs));
    return this.request('GET', `/find/file?${params}`);
  }

  async findSymbols(query) {
    return this.request('GET', `/find/symbol?query=${encodeURIComponent(query)}`);
  }

  // ========== 配置 ==========
  
  async getConfig() {
    return this.request('GET', '/config');
  }

  async updateConfig(updates) {
    return this.request('PATCH', '/config', updates);
  }

  async getProviders() {
    return this.request('GET', '/config/providers');
  }

  async listProviders() {
    return this.request('GET', '/provider');
  }

  async getProviderAuth() {
    return this.request('GET', '/provider/auth');
  }

  async setAuth(providerID, credentials) {
    return this.request('PUT', `/auth/${providerID}`, credentials);
  }

  async removeAuth(providerID) {
    return this.request('DELETE', `/auth/${providerID}`);
  }

  // ========== 代理/命令/技能 ==========
  
  async listAgents() {
    return this.request('GET', '/agent');
  }

  async listCommands() {
    return this.request('GET', '/command');
  }

  async listSkills() {
    return this.request('GET', '/skill');
  }

  // ========== MCP ==========
  
  async getMCPStatus() {
    return this.request('GET', '/mcp');
  }

  async addMCPServer(name, config) {
    return this.request('POST', '/mcp', { name, config });
  }

  async connectMCPServer(name) {
    return this.request('POST', `/mcp/${name}/connect`);
  }

  async disconnectMCPServer(name) {
    return this.request('POST', `/mcp/${name}/disconnect`);
  }

  // ========== 其他 ==========
  
  async getVCSInfo() {
    return this.request('GET', '/vcs');
  }

  async getPathInfo() {
    return this.request('GET', '/path');
  }

  async getLSPStatus() {
    return this.request('GET', '/lsp');
  }

  async getFormatterStatus() {
    return this.request('GET', '/formatter');
  }

  async listPermissions() {
    return this.request('GET', '/permission');
  }

  async respondToPermission(sessionID, permissionID, response, remember = false) {
    return this.request('POST', `/session/${sessionID}/permissions/${permissionID}`, {
      response,
      remember,
    });
  }

  async listPTY() {
    return this.request('GET', '/pty');
  }

  async createPTY() {
    return this.request('POST', '/pty');
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { OpenCodeAPI };
}

// 使用示例
/*
const client = new OpenCodeAPI({
  baseURL: process.env.OPENCODE_SERVER_BASE_URL || 'http://127.0.0.1:4096',
  username: process.env.OPENCODE_SERVER_USERNAME || 'opencode',
  password: process.env.OPENCODE_SERVER_PASSWORD
});

// 健康检查
const health = await client.health();
console.log(health);

// 创建会话
const session = await client.createSession({ title: '我的会话' });
console.log('Session ID:', session.id);

// 发送消息
const response = await client.sendMessage(session.id, {
  parts: [{ type: 'text', text: '你好！' }]
});
console.log(response);

// 列出文件
const files = await client.listFiles('.');
console.log(files);
*/
