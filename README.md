# PS5 Controller TikTok Scroller

**[English](#english) · [中文](#中文) · [العربية](#العربية)**

---

## English

Use a PS5 DualSense controller as a mouse on Windows to scroll TikTok from your couch.

### Requirements
- Windows 10 / 11
- Python 3.9 or newer
- A PS5 DualSense controller connected over USB or Bluetooth

### Getting started
1. Download or clone this repository.
2. Double-click `run.bat`. It installs the dependency (`pygame-ce`) and starts the program.
   Or run it yourself:
   ```
   pip install -r requirements.txt
   python dualsense_mouse.py
   ```
3. Open TikTok in your browser and put the cursor over the video.

The program keeps reading the controller while the browser is the active window.

### Controls
| Input | Action |
|---|---|
| Left stick | Move the cursor (hold **L2** for slow, precise movement) |
| Right stick flick down / up | Next / previous video |
| D-pad down / up, R1 / L1 | Next / previous video (hold to keep skipping) |
| Cross (✕) | Left click (hold to drag) |
| Circle (○) | Right click |
| Triangle (△) | Like |
| Square (□) | Mute / unmute |
| R3 (press the right stick) | Play / pause |
| Options | Pause or resume the controller mapping |
| PS button | Quit |

### Notes
- Switching videos sends a mouse-wheel scroll, so the cursor must be over the video.
- Like, mute and play/pause use TikTok's keyboard shortcuts, so click the TikTok page once first.
- If nothing happens, Steam may have taken over the controller. Close Steam or turn off its PlayStation controller support.
- Change the settings at the top of `dualsense_mouse.py` (`CURSOR_MAX_SPEED`, `STICK_DEADZONE`, `INVERT_SCROLL` and the repeat timing) to adjust it.

---

## 中文

在 Windows 上把 PS5 DualSense 手柄当作鼠标使用，躺在沙发上就能刷 TikTok。

### 运行要求
- Windows 10 / 11
- Python 3.9 或更高版本
- 通过 USB 或蓝牙连接的 PS5 DualSense 手柄

### 快速开始
1. 下载或克隆本仓库。
2. 双击 `run.bat`，它会自动安装依赖（`pygame-ce`）并启动程序。
   也可以手动运行：
   ```
   pip install -r requirements.txt
   python dualsense_mouse.py
   ```
3. 在浏览器中打开 TikTok，并将光标放在视频上。

即使浏览器是当前活动窗口，程序也会持续读取手柄输入。

### 按键说明
| 按键 | 功能 |
|---|---|
| 左摇杆 | 移动光标（按住 **L2** 可慢速精确移动） |
| 右摇杆向下 / 向上拨动 | 下一个 / 上一个视频 |
| 方向键下 / 上，R1 / L1 | 下一个 / 上一个视频（按住可连续切换） |
| ✕ 键 | 鼠标左键（按住可拖动） |
| ○ 键 | 鼠标右键 |
| △ 键 | 点赞 |
| □ 键 | 静音 / 取消静音 |
| R3（按下右摇杆） | 播放 / 暂停 |
| Options 键 | 暂停或恢复手柄映射 |
| PS 键 | 退出程序 |

### 注意事项
- 切换视频是通过发送鼠标滚轮实现的，因此光标必须位于视频上方。
- 点赞、静音和播放/暂停使用的是 TikTok 的键盘快捷键，请先点击一次 TikTok 页面。
- 如果没有任何反应，可能是 Steam 占用了手柄。请关闭 Steam 或关闭其 PlayStation 手柄支持。
- 可以修改 `dualsense_mouse.py` 顶部的设置（`CURSOR_MAX_SPEED`、`STICK_DEADZONE`、`INVERT_SCROLL` 以及连按时间）进行调整。

---

## العربية

<div dir="rtl">

استخدم يد تحكم PS5 DualSense كفأرة على ويندوز لتصفح تيك توك وأنت مسترخٍ على الأريكة.

### المتطلبات
- ويندوز 10 / 11
- بايثون 3.9 أو أحدث
- يد تحكم PS5 DualSense متصلة عبر USB أو البلوتوث

### طريقة التشغيل
1. حمّل هذا المستودع أو انسخه.
2. انقر نقرًا مزدوجًا على `run.bat`، وسيقوم بتثبيت المكتبة المطلوبة (`pygame-ce`) وتشغيل البرنامج.
   أو شغّله يدويًا:

</div>

```
pip install -r requirements.txt
python dualsense_mouse.py
```

<div dir="rtl">

3. افتح تيك توك في المتصفح وضع المؤشر فوق الفيديو.

يستمر البرنامج في قراءة يد التحكم حتى عندما يكون المتصفح هو النافذة النشطة.

### أزرار التحكم
| الزر | الوظيفة |
|---|---|
| العصا اليسرى | تحريك المؤشر (اضغط مطولًا على **L2** لحركة بطيئة ودقيقة) |
| تحريك العصا اليمنى للأسفل / للأعلى | الفيديو التالي / السابق |
| الأسهم للأسفل / للأعلى، R1 / L1 | الفيديو التالي / السابق (اضغط مطولًا للتنقل المستمر) |
| زر ✕ | النقر الأيسر (اضغط مطولًا للسحب) |
| زر ○ | النقر الأيمن |
| زر △ | إعجاب |
| زر □ | كتم الصوت / إلغاء الكتم |
| R3 (الضغط على العصا اليمنى) | تشغيل / إيقاف مؤقت |
| زر Options | إيقاف أو استئناف عمل يد التحكم |
| زر PS | إغلاق البرنامج |

### ملاحظات
- التنقل بين الفيديوهات يتم عبر إرسال تمرير بعجلة الفأرة، لذا يجب أن يكون المؤشر فوق الفيديو.
- الإعجاب وكتم الصوت والتشغيل/الإيقاف تستخدم اختصارات لوحة المفاتيح في تيك توك، لذا انقر على صفحة تيك توك مرة واحدة أولًا.
- إذا لم يحدث شيء، فقد يكون Steam قد استحوذ على يد التحكم. أغلق Steam أو عطّل دعمه ليد تحكم PlayStation.
- يمكنك تعديل الإعدادات في أعلى ملف `dualsense_mouse.py` (`CURSOR_MAX_SPEED` و`STICK_DEADZONE` و`INVERT_SCROLL` وتوقيت التكرار).

</div>
