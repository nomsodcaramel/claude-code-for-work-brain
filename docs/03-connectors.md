# 3 · ต่อ Connectors (ไม่บังคับ)

**Connector** ทำให้ Claude ใช้บริการอื่นของเราได้ เช่น อ่านปฏิทิน เปิดหน้า Notion ส่งข้อความ Slack
ไม่ต่อก็ใช้ Claude Code กับส่วนจำได้ครบ

## ก่อนต่อ อ่านข้อนี้

- ต่อแล้ว Claude **อ่านและทำงานในบัญชีนั้นได้จริง** เช่น อ่านนัดทั้งหมดในปฏิทิน หรือส่งข้อความในชื่อเรา
- **บัญชีบริษัท ถามฝ่าย IT ก่อน** ว่าอนุญาตไหม
- ต่อเฉพาะบริการที่จะใช้จริง ไม่ใช้แล้วเลิกเชื่อมได้เสมอ
- ก่อนกดอนุญาตให้ Claude ทำอะไรในบริการนั้น อ่านก่อนทุกครั้งว่าจะทำอะไร

## ต่อใน Claude Code (ฝั่ง Code)

1. ใน session แบบ **Local** กดปุ่ม **+** ข้างช่องพิมพ์
2. เลือก **Connectors**
3. เลือกบริการ เช่น Google Calendar, Notion, Slack, GitHub
4. Sign in บัญชีของบริการนั้น แล้วกดอนุญาต
5. ลองถาม **ตอนนี้ต่อ connector อะไรไว้บ้าง**

ต่อก่อนเริ่มงานหรือระหว่างคุยก็ได้

## ต่อจาก claude.ai (ใช้ได้ทั้ง Chat และ Code)

connector ที่ต่อไว้ที่ [claude.ai/customize/connectors](https://claude.ai/customize/connectors)
ใช้ใน Claude Code ได้ด้วย เมื่อเรา Sign in Claude Code ด้วยบัญชี claude.ai เดียวกัน

## จัดการ หรือเลิกเชื่อม

- ในแอป: **Settings** → **Connectors**
- หรือกด **+** ข้างช่องพิมพ์ → **Connectors** → **Manage connectors**

## ใช้กับส่วนจำ

ตัวอย่างสั่งงานเมื่อต่อ Google Calendar แล้ว

- **ดูปฏิทินพรุ่งนี้ว่ามีประชุมอะไร แล้วบอกว่าเรื่องไหนเคยตัดสินไปแล้วใน decision-log.md**
- **สัปดาห์นี้มีนัดกับใครบ้าง เทียบกับรายชื่อใน users/ ว่าใครยังไม่ได้คุย**

## ข้อจำกัดที่ควรรู้

- ปุ่ม **+** → Connectors ใช้ได้ใน session แบบ **Local** (และ SSH) ไม่มีใน session แบบ Cloud
- ทีมบนแพ็กเกจ Team หรือ Enterprise: ผู้ดูแลระบบของทีมเป็นคนเพิ่ม connector ที่ claude.ai
- บริการที่ไม่มีในรายการ ต่อเองได้แบบ MCP server (สำหรับคนที่ถนัดเทคนิค) ดู
  [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)

---
ที่มา: [Use Claude Code Desktop · Connect external tools](https://code.claude.com/docs/en/desktop) ·
[MCP · Use MCP servers from Claude.ai](https://code.claude.com/docs/en/mcp) · อ่านเมื่อ 23 ก.ย. 2569
