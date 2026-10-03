const { createApp } = Vue;

createApp({
    data() {
        return {
            loggedIn: false,
            username: '',
            password: '',
            authError: '',
            userId: null,
            conversations: [],
            currentId: null,
            messages: [],
            draft: '',
            loading: false,
            view: 'chat',
            docs: [],
        };
    },
    methods: {
        async doLogin() { await this.authenticate('/auth/login'); },
        async doRegister() { await this.authenticate('/auth/register'); },
        async authenticate(path) {
            this.authError = '';
            try {
                const r = await fetch(path, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: this.username, password: this.password }),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || '认证失败');
                this.userId = data.user_id;
                this.loggedIn = true;
                await this.loadConversations();
                this.newChat();
            } catch (e) { this.authError = e.message; }
        },
        async loadConversations() {
            const r = await fetch('/conversations' + (this.userId ? '?user_id=' + this.userId : ''));
            if (r.ok) this.conversations = await r.json();
        },
        newChat() { this.currentId = null; this.messages = []; this.draft = ''; this.view = 'chat'; },
        async openKnowledge() {
            this.view = 'knowledge';
            const r = await fetch('/admin/documents');
            if (r.ok) this.docs = await r.json();
        },
        async onUpload(e) {
            const file = e.target.files[0];
            if (!file) return;
            const fd = new FormData();
            fd.append('file', file);
            const r = await fetch('/admin/upload', { method: 'POST', body: fd });
            if (r.ok) { await this.openKnowledge(); }
            else { alert('上传失败：' + ((await r.json()).detail || r.status)); }
            e.target.value = '';
        },
        async onDelete(d) {
            if (!confirm('确认删除文档「' + d.title + '」？')) return;
            const r = await fetch('/admin/documents/' + d.id, { method: 'DELETE' });
            if (r.ok) await this.openKnowledge();
        },
        async openConversation(id) {
            this.currentId = id;
            const r = await fetch(`/conversations/${id}`);
            if (r.ok) this.messages = (await r.json()).map(m => ({ role: m.role, content: m.content, streaming: false }));
        },
        escapeHtml(s) {
            return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        },
        renderMd(text) {
            const html = marked.parse(text || '');
            return DOMPurify.sanitize(html);
        },
        bubbleHtml(m) {
            return m.streaming ? '<p>' + this.escapeHtml(m.content) + '</p>' : this.renderMd(m.content);
        },
        scrollBottom() {
            this.$nextTick(() => {
                const box = this.$refs.msgBox;
                if (box) box.scrollTop = box.scrollHeight;
            });
        },
        async send() {
            const text = this.draft.trim();
            if (!text || this.loading) return;
            this.messages.push({ role: 'user', content: text, streaming: false });
            this.draft = '';
            this.loading = true;
            const assistantMsg = { role: 'assistant', content: '', intent: '', streaming: true };
            this.messages.push(assistantMsg);
            try {
                const resp = await fetch('/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, conversation_id: this.currentId, user_id: this.userId }),
                });
                if (!resp.ok) throw new Error('请求失败 ' + resp.status);
                const reader = resp.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split('\n\n');
                    buffer = parts.pop();
                    for (const part of parts) {
                        const line = part.trim();
                        if (!line.startsWith('data:')) continue;
                        const data = JSON.parse(line.slice(5).trim());
                        if (data.intent) assistantMsg.intent = data.intent;
                        if (data.token) assistantMsg.content += data.token;
                        if (data.conversation_id) this.currentId = data.conversation_id;
                        if (data.error) assistantMsg.content += '\n[错误] ' + data.error;
                    }
                    this.scrollBottom();
                }
                assistantMsg.streaming = false;
                await this.loadConversations();
            } catch (e) {
                assistantMsg.content = assistantMsg.content || ('出错了：' + e.message);
                assistantMsg.streaming = false;
            } finally {
                this.loading = false;
                this.scrollBottom();
                this.$nextTick(() => { if (window.hljs) hljs.highlightAll(); });
            }
        },
        intentLabel(i) {
            const map = { qa: '校园问答', life: '生活服务', academic: '教务查询', study: '学习辅导', psychology: '心理陪伴', planning: '学习规划' };
            return map[i] || i;
        },
        logout() { this.loggedIn = false; this.conversations = []; this.messages = []; this.currentId = null; },
    },
}).mount('#app');
