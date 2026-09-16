const messages = document.querySelector('#messages');
const form = document.querySelector('#chat-form');
const input = document.querySelector('#message-input');
const sendButton = document.querySelector('#send-button');
const resetButton = document.querySelector('#reset-button');
const sessionBadge = document.querySelector('#session-badge');
const providerSelect = document.querySelector('#provider-select');
const modelSelect = document.querySelector('#model-select');
const versionSelect = document.querySelector('#version-select');
const applyConfigButton = document.querySelector('#apply-config');
const customModelInput = document.querySelector('#custom-model');
let providerModels = {};

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#039;', '"':'&quot;' }[char]));
const json = (value) => escapeHtml(JSON.stringify(value ?? {}, null, 2));
const time = () => new Intl.DateTimeFormat('vi-VN', { hour: '2-digit', minute: '2-digit' }).format(new Date());

function scrollDown() { messages.scrollTop = messages.scrollHeight; }
function addMessage(role, text, status = null) {
  const item = document.createElement('article');
  item.className = `message ${role}`;
  item.innerHTML = `<div class="bubble">${escapeHtml(text)}</div><span class="meta">${role === 'user' ? 'Bạn' : 'IT Helpdesk'} · ${time()}</span>`;
  if (status && status !== 'answered') {
    const label = document.createElement('span');
    label.className = `status ${status}`;
    label.textContent = ({ waiting_for_user:'Cần bổ sung hoặc xác nhận', provider_error:'Lỗi kết nối provider', max_tool_rounds:'Đã dừng để đảm bảo an toàn' })[status] || status;
    item.append(label);
  }
  messages.append(item); scrollDown(); return item;
}
function addTrace(rounds) {
  if (!rounds?.some((round) => round.tool_calls?.length || round.tool_results?.length)) return;
  const node = document.querySelector('#trace-template').content.firstElementChild.cloneNode(true);
  const count = rounds.reduce((total, round) => total + (round.tool_calls?.length || 0), 0);
  node.querySelector('small').textContent = `(${count} tool call${count === 1 ? '' : 's'})`;
  const container = node.querySelector('.trace-content');
  rounds.forEach((round) => {
    if (!round.tool_calls?.length && !round.tool_results?.length) return;
    const section = document.createElement('section'); section.className = 'round';
    section.innerHTML = `<p class="round-title">ROUND ${round.round}</p>`;
    const results = round.tool_results || [];
    (round.tool_calls || []).forEach((call, index) => {
      const result = results[index] || null;
      const event = document.createElement('div'); event.className = 'tool-event';
      event.innerHTML = `<p class="tool-name">${escapeHtml(call.name)}</p><p class="json-label">ARGUMENTS</p><pre>${json(call.args)}</pre>${result ? `<p class="json-label">RESULT${result.result?.error ? ' / ERROR' : ''}</p><pre>${json(result.result)}</pre>` : ''}`;
      section.append(event);
    });
    container.append(section);
  });
  messages.append(node); scrollDown();
}
function setBusy(busy) { sendButton.disabled = busy; input.disabled = busy; resetButton.disabled = busy; applyConfigButton.disabled = busy; }
async function api(path, body) {
  const options = body ? { method:'POST', headers:{ 'Content-Type':'application/json' }, body:JSON.stringify(body) } : {};
  const response = await fetch(path, options); const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || 'Yêu cầu không thành công.'); return payload;
}
function populateModels(selectedModel) { const models = providerModels[providerSelect.value] || []; modelSelect.innerHTML = `${models.map((model) => `<option value="${model}">${model}</option>`).join('')}<option value="__custom__">Model khác…</option>`; const known = models.includes(selectedModel); modelSelect.value = known ? selectedModel : '__custom__'; customModelInput.hidden = known; customModelInput.value = known ? '' : (selectedModel || ''); }
async function loadConfig() {
  try { const [config, options] = await Promise.all([api('/api/config'), api('/api/options')]); providerModels = options.providers;
    providerSelect.innerHTML = Object.keys(providerModels).map((provider) => `<option value="${provider}" ${options.provider_configured[provider] ? '' : 'disabled'}>${provider}${options.provider_configured[provider] ? '' : ' · thiếu API key'}</option>`).join('');
    versionSelect.innerHTML = options.versions.map((version) => `<option value="${version}">${version.toUpperCase()}</option>`).join('');
    providerSelect.value = config.provider; versionSelect.value = config.version; populateModels(config.model);
    document.querySelector('#provider').textContent = config.provider || '—';
    document.querySelector('#model').textContent = config.model || 'Mặc định';
    document.querySelector('#artifact').textContent = config.artifact_version;
  } catch { document.querySelector('#provider').textContent = 'Không thể tải'; }
}
providerSelect.addEventListener('change', () => populateModels());
modelSelect.addEventListener('change', () => { customModelInput.hidden = modelSelect.value !== '__custom__'; if (!customModelInput.hidden) customModelInput.focus(); });
applyConfigButton.addEventListener('click', async () => { const model = modelSelect.value === '__custom__' ? customModelInput.value.trim() : modelSelect.value; if (!model) { addMessage('assistant', 'Hãy nhập tên model trước khi áp dụng cấu hình.', 'provider_error'); return; } setBusy(true); try { const result = await api('/api/configure', { provider:providerSelect.value, model, version:versionSelect.value }); messages.innerHTML = ''; addMessage('assistant', result.message); document.querySelector('#provider').textContent = result.provider; document.querySelector('#model').textContent = result.model; document.querySelector('#artifact').textContent = result.artifact_version; sessionBadge.textContent = `Transcript · ${result.transcript_id}`; } catch (error) { addMessage('assistant', error.message, 'provider_error'); } finally { setBusy(false); input.focus(); } });
form.addEventListener('submit', async (event) => {
  event.preventDefault(); const message = input.value.trim(); if (!message) return;
  addMessage('user', message); input.value = ''; input.style.height = ''; setBusy(true);
  const typing = addMessage('assistant', 'Agent đang phân tích và gọi công cụ thật…'); typing.classList.add('typing');
  try { const result = await api('/api/chat', { message }); typing.remove(); typing.querySelector('.bubble').textContent = result.assistant_text || 'Agent chưa có phản hồi.';
    const meta = typing.querySelector('.meta'); meta.textContent = `IT Helpdesk · ${time()}`;
    if (result.status !== 'answered') { const label = document.createElement('span'); label.className = `status ${result.status}`; label.textContent = ({ waiting_for_user:'Cần bổ sung hoặc xác nhận', provider_error:'Lỗi kết nối provider', max_tool_rounds:'Đã dừng để đảm bảo an toàn' })[result.status] || result.status; typing.append(label); }
    addTrace(result.rounds); sessionBadge.textContent = `Transcript · ${result.transcript_id}`;
  } catch (error) { typing.remove(); addMessage('assistant', error.message, 'provider_error'); }
  finally { setBusy(false); input.focus(); scrollDown(); }
});
input.addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); } });
input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight, 180)}px`; });
resetButton.addEventListener('click', async () => { setBusy(true); try { const result = await api('/api/reset', {}); messages.innerHTML = ''; addMessage('assistant', 'Đã bắt đầu cuộc trò chuyện mới. Transcript của phiên trước vẫn được lưu.'); sessionBadge.textContent = `Transcript · ${result.transcript_id}`; } catch (error) { addMessage('assistant', error.message, 'provider_error'); } finally { setBusy(false); input.focus(); } });
loadConfig();
