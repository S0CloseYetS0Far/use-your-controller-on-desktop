# PS5 Controller TikTok Scroller

**[English](#english) · [中文](#中文) · [العربية](#العربية)**

---

## English

Use a PS5 DualSense controller as a mouse on Windows. It has three modes: **Standard** (a normal mouse), **TikTok** (scroll videos from your couch) and **Browser** (switch tabs and type with an on-screen keyboard).

### Requirements
- Windows 10 / 11
- Python 3.9 or newer
- A PS5 DualSense controller connected over USB or Bluetooth

### Getting started
1. Download or clone this repository.
2. Double-click `run.bat`. It installs the dependencies (`pygame-ce`, `comtypes`) and starts the program.
   Or run it yourself:
   ```
   pip install -r requirements.txt
   python dualsense_mouse.py
   ```
3. Press **Create** (the small button left of the touchpad) to switch between Standard, TikTok and Browser mode. A message at the top of the screen shows the current mode.

The program keeps reading the controller while another window, such as your browser, is the active window.

### Controls in every mode
| Input | Action |
|---|---|
| Left stick | Move the cursor (hold **L2** for slow, precise movement) |
| Cross (✕) | Left click (hold to drag) |
| Circle (○) | Right click |
| Touchpad click | Open / close the on-screen keyboard |
| Create | Switch mode |
| Options | Pause or resume the controller mapping |
| PS button | Quit |

### Standard mode
| Input | Action |
|---|---|
| Right stick | Scroll (up/down and left/right) |
| D-pad | Arrow keys |
| L1 / R1 | Mouse back / forward buttons |
| Square (□) | Middle click |
| Triangle (△) | Open the on-screen keyboard |

### TikTok mode
| Input | Action |
|---|---|
| Right stick flick down / up | Next / previous video |
| D-pad down / up, R1 / L1 | Next / previous video (hold to keep skipping) |
| Triangle (△) | Like |
| Square (□) | Mute / unmute |
| R3 (press the right stick) | Play / pause |

### Browser mode
| Input | Action |
|---|---|
| Right stick | Scroll the page |
| L1 / R1 | Previous / next tab |
| D-pad left / right | Back / forward |
| D-pad up | Reload |
| D-pad down (hold) | Close tab |
| Triangle (△) | Go to the address bar and open the keyboard (search or type a URL) |
| Square (□) | New tab and open the keyboard |
| R3 (press the right stick) | Middle click (open a link in a new tab) |

In Browser mode the keyboard **pops up by itself** when you click into a search box or any other text field, and closes again once you leave it.

### On-screen keyboard
| Input | Action |
|---|---|
| D-pad / left stick | Move around the keys |
| Cross (✕) | Type the highlighted key |
| Square (□) | Backspace |
| Triangle (△) | Space |
| R2 | Enter (and close the keyboard) |
| L1 / R1 | Move the text cursor left / right |
| L2 | Shift (press twice for caps lock) |
| L3 (press the left stick) | Switch layout: English → Arabic → symbols |
| Circle (○) or touchpad | Close the keyboard |

The keyboard never takes focus away from your browser, so what you type goes straight into the text box.

### Notes
- In TikTok mode, switching videos sends a mouse-wheel scroll, so the cursor must be over the video.
- Like, mute and play/pause use TikTok's keyboard shortcuts, so click the TikTok page once first.
- If nothing happens, Steam may have taken over the controller. Close Steam or turn off its PlayStation controller support.
- Change the settings at the top of `dualsense_mouse.py` to adjust it, for example `DEFAULT_MODE`, `CURSOR_MAX_SPEED`, `SCROLL_SPEED`, `STICK_DEADZONE` and `AUTO_KEYBOARD_MODES`.

---

## 中文

在 Windows 上把 PS5 DualSense 手柄当作鼠标使用。共有三种模式：**标准模式**（普通鼠标）、**TikTok 模式**（躺在沙发上刷视频）和**浏览器模式**（切换标签页，并用屏幕键盘打字）。

### 运行要求
- Windows 10 / 11
- Python 3.9 或更高版本
- 通过 USB 或蓝牙连接的 PS5 DualSense 手柄

### 快速开始
1. 下载或克隆本仓库。
2. 双击 `run.bat`，它会自动安装依赖（`pygame-ce`、`comtypes`）并启动程序。
   也可以手动运行：
   ```
   pip install -r requirements.txt
   python dualsense_mouse.py
   ```
3. 按 **Create 键**（触摸板左侧的小按钮）在标准、TikTok 和浏览器模式之间切换。屏幕顶部会显示当前模式。

即使浏览器等其他窗口处于活动状态，程序也会持续读取手柄输入。

### 所有模式通用
| 按键 | 功能 |
|---|---|
| 左摇杆 | 移动光标（按住 **L2** 可慢速精确移动） |
| ✕ 键 | 鼠标左键（按住可拖动） |
| ○ 键 | 鼠标右键 |
| 按下触摸板 | 打开 / 关闭屏幕键盘 |
| Create 键 | 切换模式 |
| Options 键 | 暂停或恢复手柄映射 |
| PS 键 | 退出程序 |

### 标准模式
| 按键 | 功能 |
|---|---|
| 右摇杆 | 滚动（上下和左右） |
| 方向键 | 键盘方向键 |
| L1 / R1 | 鼠标后退 / 前进键 |
| □ 键 | 鼠标中键 |
| △ 键 | 打开屏幕键盘 |

### TikTok 模式
| 按键 | 功能 |
|---|---|
| 右摇杆向下 / 向上拨动 | 下一个 / 上一个视频 |
| 方向键下 / 上，R1 / L1 | 下一个 / 上一个视频（按住可连续切换） |
| △ 键 | 点赞 |
| □ 键 | 静音 / 取消静音 |
| R3（按下右摇杆） | 播放 / 暂停 |

### 浏览器模式
| 按键 | 功能 |
|---|---|
| 右摇杆 | 滚动页面 |
| L1 / R1 | 上一个 / 下一个标签页 |
| 方向键左 / 右 | 后退 / 前进 |
| 方向键上 | 刷新 |
| 方向键下（按住） | 关闭标签页 |
| △ 键 | 跳到地址栏并打开键盘（搜索或输入网址） |
| □ 键 | 新建标签页并打开键盘 |
| R3（按下右摇杆） | 鼠标中键（在新标签页中打开链接） |

在浏览器模式下，点击搜索框或任何输入框时，键盘会**自动弹出**；离开输入框后会自动关闭。

### 屏幕键盘
| 按键 | 功能 |
|---|---|
| 方向键 / 左摇杆 | 在按键之间移动 |
| ✕ 键 | 输入选中的按键 |
| □ 键 | 退格 |
| △ 键 | 空格 |
| R2 | 回车（并关闭键盘） |
| L1 / R1 | 将文字光标左移 / 右移 |
| L2 | Shift（按两次为大写锁定） |
| L3（按下左摇杆） | 切换布局：英文 → 阿拉伯文 → 符号 |
| ○ 键或触摸板 | 关闭键盘 |

屏幕键盘不会抢走浏览器的焦点，所以输入的文字会直接进入输入框。

### 注意事项
- 在 TikTok 模式下，切换视频是通过发送鼠标滚轮实现的，因此光标必须位于视频上方。
- 点赞、静音和播放/暂停使用的是 TikTok 的键盘快捷键，请先点击一次 TikTok 页面。
- 如果没有任何反应，可能是 Steam 占用了手柄。请关闭 Steam 或关闭其 PlayStation 手柄支持。
- 可以修改 `dualsense_mouse.py` 顶部的设置进行调整，例如 `DEFAULT_MODE`、`CURSOR_MAX_SPEED`、`SCROLL_SPEED`、`STICK_DEADZONE` 和 `AUTO_KEYBOARD_MODES`。

---

## العربية

<div dir="rtl">

استخدم يد تحكم PS5 DualSense كفأرة على ويندوز. يحتوي البرنامج على ثلاثة أوضاع: **الوضع العادي** (فأرة عادية)، و**وضع تيك توك** (تصفح الفيديوهات وأنت على الأريكة)، و**وضع المتصفح** (التنقل بين علامات التبويب والكتابة بلوحة مفاتيح على الشاشة).

### المتطلبات
- ويندوز 10 / 11
- بايثون 3.9 أو أحدث
- يد تحكم PS5 DualSense متصلة عبر USB أو البلوتوث

### طريقة التشغيل
1. حمّل هذا المستودع أو انسخه.
2. انقر نقرًا مزدوجًا على `run.bat`، وسيقوم بتثبيت المكتبات المطلوبة (`pygame-ce` و`comtypes`) وتشغيل البرنامج.
   أو شغّله يدويًا:

</div>

```
pip install -r requirements.txt
python dualsense_mouse.py
```

<div dir="rtl">

3. اضغط على زر **Create** (الزر الصغير على يسار لوحة اللمس) للتبديل بين الوضع العادي ووضع تيك توك ووضع المتصفح. تظهر رسالة أعلى الشاشة توضح الوضع الحالي.

يستمر البرنامج في قراءة يد التحكم حتى عندما تكون نافذة أخرى، مثل المتصفح، هي النافذة النشطة.

### أزرار مشتركة في كل الأوضاع
| الزر | الوظيفة |
|---|---|
| العصا اليسرى | تحريك المؤشر (اضغط مطولًا على **L2** لحركة بطيئة ودقيقة) |
| زر ✕ | النقر الأيسر (اضغط مطولًا للسحب) |
| زر ○ | النقر الأيمن |
| الضغط على لوحة اللمس | فتح / إغلاق لوحة المفاتيح على الشاشة |
| زر Create | تبديل الوضع |
| زر Options | إيقاف أو استئناف عمل يد التحكم |
| زر PS | إغلاق البرنامج |

### الوضع العادي
| الزر | الوظيفة |
|---|---|
| العصا اليمنى | التمرير (للأعلى والأسفل ولليمين واليسار) |
| الأسهم | أسهم لوحة المفاتيح |
| L1 / R1 | زرّا الرجوع / التقدم في الفأرة |
| زر □ | النقر الأوسط |
| زر △ | فتح لوحة المفاتيح على الشاشة |

### وضع تيك توك
| الزر | الوظيفة |
|---|---|
| تحريك العصا اليمنى للأسفل / للأعلى | الفيديو التالي / السابق |
| الأسهم للأسفل / للأعلى، R1 / L1 | الفيديو التالي / السابق (اضغط مطولًا للتنقل المستمر) |
| زر △ | إعجاب |
| زر □ | كتم الصوت / إلغاء الكتم |
| R3 (الضغط على العصا اليمنى) | تشغيل / إيقاف مؤقت |

### وضع المتصفح
| الزر | الوظيفة |
|---|---|
| العصا اليمنى | تمرير الصفحة |
| L1 / R1 | علامة التبويب السابقة / التالية |
| السهم الأيسر / الأيمن | رجوع / تقدم |
| السهم للأعلى | إعادة تحميل الصفحة |
| السهم للأسفل (ضغط مطوّل) | إغلاق علامة التبويب |
| زر △ | الانتقال إلى شريط العنوان وفتح لوحة المفاتيح (للبحث أو كتابة رابط) |
| زر □ | علامة تبويب جديدة وفتح لوحة المفاتيح |
| R3 (الضغط على العصا اليمنى) | النقر الأوسط (فتح الرابط في علامة تبويب جديدة) |

في وضع المتصفح **تظهر لوحة المفاتيح تلقائيًا** عند النقر على مربع البحث أو أي حقل نصي، وتختفي عند الخروج منه.

### لوحة المفاتيح على الشاشة
| الزر | الوظيفة |
|---|---|
| الأسهم / العصا اليسرى | التنقل بين المفاتيح |
| زر ✕ | كتابة المفتاح المحدد |
| زر □ | حذف حرف |
| زر △ | مسافة |
| R2 | إدخال (Enter) وإغلاق لوحة المفاتيح |
| L1 / R1 | تحريك مؤشر الكتابة لليسار / لليمين |
| L2 | Shift (اضغط مرتين لتثبيت الأحرف الكبيرة) |
| L3 (الضغط على العصا اليسرى) | تبديل اللغة: الإنجليزية ← العربية ← الرموز |
| زر ○ أو لوحة اللمس | إغلاق لوحة المفاتيح |

لوحة المفاتيح لا تأخذ التركيز من المتصفح، لذلك يُكتب النص مباشرة في الحقل النصي.

### ملاحظات
- في وضع تيك توك، يتم التنقل بين الفيديوهات عبر إرسال تمرير بعجلة الفأرة، لذا يجب أن يكون المؤشر فوق الفيديو.
- الإعجاب وكتم الصوت والتشغيل/الإيقاف تستخدم اختصارات لوحة المفاتيح في تيك توك، لذا انقر على صفحة تيك توك مرة واحدة أولًا.
- إذا لم يحدث شيء، فقد يكون Steam قد استحوذ على يد التحكم. أغلق Steam أو عطّل دعمه ليد تحكم PlayStation.
- يمكنك تعديل الإعدادات في أعلى ملف `dualsense_mouse.py`، مثل `DEFAULT_MODE` و`CURSOR_MAX_SPEED` و`SCROLL_SPEED` و`STICK_DEADZONE` و`AUTO_KEYBOARD_MODES`.

</div>
