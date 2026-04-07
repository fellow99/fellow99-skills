"""
opencode_api.py - opencode REST API Python 客户端

用法:
    import os
    from opencode_api import OpenCodeAPI
    
    client = OpenCodeAPI(
        base_url=os.getenv('OPENCODE_SERVER_BASE_URL', 'http://127.0.0.1:4096'),
        username=os.getenv('OPENCODE_SERVER_USERNAME', 'opencode'),
        password=os.getenv('OPENCODE_SERVER_PASSWORD')  # 可选
    )
    
    # 健康检查
    health = client.health()
    
    # 创建会话
    session = client.create_session(title='我的会话')
    
    # 发送消息
    response = client.send_message(session['id'], '你好！')
"""

import requests
import os
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode


class OpenCodeAPI:
    def __init__(
        self,
        base_url: str = None,
        username: str = None,
        password: Optional[str] = None,
    ):
        self.base_url = (base_url or os.getenv('OPENCODE_SERVER_BASE_URL', 'http://127.0.0.1:4096')).rstrip('/')
        self.username = username or os.getenv('OPENCODE_SERVER_USERNAME', 'opencode')
        self.password = password or os.getenv('OPENCODE_SERVER_PASSWORD')
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        
        if password:
            self.session.auth = (username, password)
        
        self.session.headers.update({'Content-Type': 'application/json'})

    def _request(self, method: str, path: str, json: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, json=json, params=params)
        response.raise_for_status()
        
        if response.status_code == 204:
            return None
        
        return response.json()

    # ========== 全局端点 ==========
    
    def health(self) -> Dict:
        """健康检查"""
        return self._request('GET', '/global/health')

    def get_global_config(self) -> Dict:
        """获取全局配置"""
        return self._request('GET', '/global/config')

    def update_global_config(self, config: Dict) -> Dict:
        """更新全局配置"""
        return self._request('PATCH', '/global/config', json=config)

    def dispose(self) -> bool:
        """释放所有资源"""
        return self._request('POST', '/global/dispose')

    # ========== 会话管理 ==========
    
    def list_sessions(self) -> List[Dict]:
        """列出所有会话"""
        return self._request('GET', '/session')

    def create_session(self, parent_id: Optional[str] = None, title: Optional[str] = None) -> Dict:
        """创建新会话"""
        body = {}
        if parent_id:
            body['parentID'] = parent_id
        if title:
            body['title'] = title
        return self._request('POST', '/session', json=body)

    def get_session(self, session_id: str) -> Dict:
        """获取会话详情"""
        return self._request('GET', f'/session/{session_id}')

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return self._request('DELETE', f'/session/{session_id}')

    def update_session(self, session_id: str, updates: Dict) -> Dict:
        """更新会话"""
        return self._request('PATCH', f'/session/{session_id}', json=updates)

    def abort_session(self, session_id: str) -> bool:
        """中止会话"""
        return self._request('POST', f'/session/{session_id}/abort')

    def fork_session(self, session_id: str, message_id: Optional[str] = None) -> Dict:
        """分叉会话"""
        body = {'messageID': message_id} if message_id else {}
        return self._request('POST', f'/session/{session_id}/fork', json=body)

    def summarize_session(self, session_id: str, provider_id: str, model_id: str) -> bool:
        """总结会话"""
        return self._request('POST', f'/session/{session_id}/summarize', json={
            'providerID': provider_id,
            'modelID': model_id
        })

    def share_session(self, session_id: str) -> Dict:
        """分享会话"""
        return self._request('POST', f'/session/{session_id}/share')

    def unshare_session(self, session_id: str) -> Dict:
        """取消分享会话"""
        return self._request('DELETE', f'/session/{session_id}/share')

    def get_session_diff(self, session_id: str, message_id: Optional[str] = None) -> List[Dict]:
        """获取会话差异"""
        params = {'messageID': message_id} if message_id else {}
        return self._request('GET', f'/session/{session_id}/diff', params=params)

    def get_session_todo(self, session_id: str) -> List[Dict]:
        """获取待办事项"""
        return self._request('GET', f'/session/{session_id}/todo')

    def get_session_children(self, session_id: str) -> List[Dict]:
        """获取子会话"""
        return self._request('GET', f'/session/{session_id}/children')

    def get_session_status(self) -> Dict:
        """获取所有会话状态"""
        return self._request('GET', '/session/status')

    # ========== 消息 ==========
    
    def list_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None, 
        before: Optional[str] = None
    ) -> List[Dict]:
        """获取消息列表"""
        params = {}
        if limit:
            params['limit'] = limit
        if before:
            params['before'] = before
        return self._request('GET', f'/session/{session_id}/message', params=params)

    def get_message(self, session_id: str, message_id: str) -> Dict:
        """获取单条消息"""
        return self._request('GET', f'/session/{session_id}/message/{message_id}')

    def send_message(
        self,
        session_id: str,
        parts: List[Dict],
        model: Optional[Dict] = None,
        agent: Optional[str] = None,
        no_reply: Optional[bool] = None,
        system: Optional[str] = None,
        variant: Optional[str] = None,
        format: Optional[Dict] = None,
    ) -> Dict:
        """发送消息"""
        body = {'parts': parts}
        if model:
            body['model'] = model
        if agent:
            body['agent'] = agent
        if no_reply is not None:
            body['noReply'] = no_reply
        if system:
            body['system'] = system
        if variant:
            body['variant'] = variant
        if format:
            body['format'] = format
        return self._request('POST', f'/session/{session_id}/message', json=body)

    def send_prompt_async(self, session_id: str, options: Dict) -> None:
        """异步发送消息（不等待响应）"""
        return self._request('POST', f'/session/{session_id}/prompt_async', json=options)

    def delete_message(self, session_id: str, message_id: str) -> bool:
        """删除消息"""
        return self._request('DELETE', f'/session/{session_id}/message/{message_id}')

    def revert_message(
        self, 
        session_id: str, 
        message_id: str, 
        part_id: Optional[str] = None
    ) -> bool:
        """回退消息"""
        body = {'messageID': message_id, 'partID': part_id} if part_id else {'messageID': message_id}
        return self._request('POST', f'/session/{session_id}/revert', json=body)

    def unrevert_messages(self, session_id: str) -> bool:
        """恢复所有回退的消息"""
        return self._request('POST', f'/session/{session_id}/unrevert')

    # ========== 命令 ==========
    
    def execute_command(
        self,
        session_id: str,
        command: str,
        arguments: Optional[Dict] = None,
        agent: Optional[str] = None,
        model: Optional[Dict] = None,
    ) -> Dict:
        """执行斜杠命令"""
        body = {'command': command, 'arguments': arguments or {}}
        if agent:
            body['agent'] = agent
        if model:
            body['model'] = model
        return self._request('POST', f'/session/{session_id}/command', json=body)

    def run_shell(
        self,
        session_id: str,
        command: str,
        agent: str,
        model: Optional[Dict] = None,
    ) -> Dict:
        """运行 shell 命令"""
        body = {'command': command, 'agent': agent}
        if model:
            body['model'] = model
        return self._request('POST', f'/session/{session_id}/shell', json=body)

    # ========== 项目 ==========
    
    def list_projects(
        self, 
        directory: Optional[str] = None, 
        workspace: Optional[str] = None
    ) -> List[Dict]:
        """列出项目"""
        params = {}
        if directory:
            params['directory'] = directory
        if workspace:
            params['workspace'] = workspace
        return self._request('GET', '/project', params=params)

    def get_current_project(
        self, 
        directory: Optional[str] = None, 
        workspace: Optional[str] = None
    ) -> Dict:
        """获取当前项目"""
        params = {}
        if directory:
            params['directory'] = directory
        if workspace:
            params['workspace'] = workspace
        return self._request('GET', '/project/current', params=params)

    def init_git(
        self, 
        directory: Optional[str] = None, 
        workspace: Optional[str] = None
    ) -> Dict:
        """初始化 git 仓库"""
        params = {}
        if directory:
            params['directory'] = directory
        if workspace:
            params['workspace'] = workspace
        return self._request('POST', '/project/git/init', params=params)

    def update_project(self, project_id: str, updates: Dict) -> Dict:
        """更新项目"""
        return self._request('PATCH', f'/project/{project_id}', json=updates)

    # ========== 文件 ==========
    
    def list_files(
        self, 
        path: str = '.',
        directory: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> List[Dict]:
        """列出文件"""
        params = {'path': path}
        if directory:
            params['directory'] = directory
        if workspace:
            params['workspace'] = workspace
        return self._request('GET', '/file', params=params)

    def read_file(
        self, 
        path: str,
        directory: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> Dict:
        """读取文件内容"""
        params = {'path': path}
        if directory:
            params['directory'] = directory
        if workspace:
            params['workspace'] = workspace
        return self._request('GET', '/file/content', params=params)

    def get_file_status(self) -> List[Dict]:
        """获取文件状态"""
        return self._request('GET', '/file/status')

    # ========== 搜索 ==========
    
    def search_text(
        self, 
        pattern: str,
        directory: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> List[Dict]:
        """搜索文本"""
        params = {'pattern': pattern}
        if directory:
            params['directory'] = directory
        if workspace:
            params['workspace'] = workspace
        return self._request('GET', '/find', params=params)

    def find_files(
        self,
        query: str,
        file_type: Optional[str] = None,
        directory: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[str]:
        """查找文件"""
        params = {'query': query}
        if file_type:
            params['type'] = file_type
        if directory:
            params['directory'] = directory
        if limit:
            params['limit'] = limit
        return self._request('GET', '/find/file', params=params)

    def find_symbols(self, query: str) -> List[Dict]:
        """查找符号"""
        return self._request('GET', '/find/symbol', params={'query': query})

    # ========== 配置 ==========
    
    def get_config(self) -> Dict:
        """获取配置"""
        return self._request('GET', '/config')

    def update_config(self, updates: Dict) -> Dict:
        """更新配置"""
        return self._request('PATCH', '/config', json=updates)

    def get_providers(self) -> Dict:
        """获取提供商和默认模型"""
        return self._request('GET', '/config/providers')

    def list_providers(self) -> Dict:
        """列出所有提供商"""
        return self._request('GET', '/provider')

    def get_provider_auth(self) -> Dict:
        """获取提供商认证方式"""
        return self._request('GET', '/provider/auth')

    def set_auth(self, provider_id: str, credentials: Dict) -> bool:
        """设置认证凭据"""
        return self._request('PUT', f'/auth/{provider_id}', json=credentials)

    def remove_auth(self, provider_id: str) -> bool:
        """移除认证凭据"""
        return self._request('DELETE', f'/auth/{provider_id}')

    # ========== 代理/命令/技能 ==========
    
    def list_agents(self) -> List[Dict]:
        """列出可用代理"""
        return self._request('GET', '/agent')

    def list_commands(self) -> List[Dict]:
        """列出可用命令"""
        return self._request('GET', '/command')

    def list_skills(self) -> List[Dict]:
        """列出可用技能"""
        return self._request('GET', '/skill')

    # ========== MCP ==========
    
    def get_mcp_status(self) -> Dict:
        """获取 MCP 服务器状态"""
        return self._request('GET', '/mcp')

    def add_mcp_server(self, name: str, config: Dict) -> Dict:
        """添加 MCP 服务器"""
        return self._request('POST', '/mcp', json={'name': name, 'config': config})

    def connect_mcp_server(self, name: str) -> Dict:
        """连接 MCP 服务器"""
        return self._request('POST', f'/mcp/{name}/connect')

    def disconnect_mcp_server(self, name: str) -> Dict:
        """断开 MCP 服务器"""
        return self._request('POST', f'/mcp/{name}/disconnect')

    # ========== 其他 ==========
    
    def get_vcs_info(self) -> Dict:
        """获取 VCS 信息"""
        return self._request('GET', '/vcs')

    def get_path_info(self) -> Dict:
        """获取路径信息"""
        return self._request('GET', '/path')

    def get_lsp_status(self) -> List[Dict]:
        """获取 LSP 状态"""
        return self._request('GET', '/lsp')

    def get_formatter_status(self) -> List[Dict]:
        """获取格式化器状态"""
        return self._request('GET', '/formatter')

    def list_permissions(self) -> List[Dict]:
        """列出权限请求"""
        return self._request('GET', '/permission')

    def respond_to_permission(
        self, 
        session_id: str, 
        permission_id: str, 
        response: str,
        remember: bool = False,
    ) -> bool:
        """响应权限请求"""
        return self._request('POST', f'/session/{session_id}/permissions/{permission_id}', json={
            'response': response,
            'remember': remember,
        })

    def list_pty(self) -> List[Dict]:
        """列出 PTY 会话"""
        return self._request('GET', '/pty')

    def create_pty(self) -> Dict:
        """创建 PTY 会话"""
        return self._request('POST', '/pty')


# 使用示例
if __name__ == '__main__':
    client = OpenCodeAPI(
        base_url=os.getenv('OPENCODE_SERVER_BASE_URL', 'http://127.0.0.1:4096'),
        username=os.getenv('OPENCODE_SERVER_USERNAME', 'opencode'),
        password=os.getenv('OPENCODE_SERVER_PASSWORD'),
    )
    
    # 健康检查
    print("健康检查:", client.health())
    
    # 列出会话
    print("会话列表:", client.list_sessions())
    
    # 创建会话
    session = client.create_session(title='测试会话')
    print("创建会话:", session)
    
    # 发送消息
    response = client.send_message(
        session['id'],
        parts=[{'type': 'text', 'text': '你好！'}]
    )
    print("消息响应:", response)
