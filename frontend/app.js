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
        };
    },
    methods: {
        async doLogin() {
            await this.authenticate('/auth/login');
        },
        async doRegister() {
            await this.authenticate('/auth/register');
        },
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
            } catch (e) {
                this.authError = e.message;
            }
        },
        async loadConversations() {
            const r = await fetch('/conversations');
            if (r.ok) this.conversations = await r.json();
        },
        async newChat() {
            this.currentId = null;
            this.messages = [];
            this.draft = '';
        },
        async openConversation(id) {
            this.currentId = id;
            const r = await fetch(`/conversations/${id}`);
            if (r.ok) this.messages = await r.json();
        },
        async send() {
            const text = this.draft.trim();
            if (!text || this.loading) return;
            this.messages.push({ role: 'user', content: text });
            this.draft = '';
            this.loading = true;
            try {
                const r = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, conversation_id: this.currentId, user_id: this.userId }),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || '请求失败');
                this.currentId = data.conversation_id;
                this.messages.push({ role: 'assistant', content: data.reply, intent: data.intent });
                await this.loadConversations();
            } catch (e) {
                this.messages.push({ role: 'assistant', content: '出错了：' + e.message });
            } finally {
                this.loading = false;
                this.$nextTick(() => {
                    const box = this.$refs.msgBox;
                    if (box) box.scrollTop = box.scrollHeight;
                });
            }
        },
        intentLabel(i) {
            const map = { qa: '校园问答', life: '生活服务', academic: '教务查询', study: '学习辅导', psychology: '心理陪伴', planning: '学习规划' };
            return map[i] || i;
        },
        logout() {
            this.loggedIn = false;
            this.conversations = [];
            this.messages = [];
            this.currentId = null;
        },
    },
}).mount('#app');
