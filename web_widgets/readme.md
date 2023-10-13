# 企微 Widget

## Json编辑器

创建一个 `fields.Json` 的字段，然后在视图中使用 `json_editor` 的 `widget`，即可使用 `json` 编辑器
```python
report_data_set = fields.Json(string="Report Data Set", translate=False, help="Report Data Set.")
```
```xml
<field name="report_data_set" widget="json_editor" options="{'mode': 'code', 'modes':['code', 'form', 'text', 'tree', 'view', 'preview']}" force_save="1" readonly="1"/>
```
> `options` 参数说明:

| 选项|   说明 |
|----------|-----:|
|mode| 默认模式 |
|modes| 模式清单，可选有： `code`, `form`, `text`, `tree`, `view`, `preview`|


## Markdown 编辑器

### 使用
```xml
<field name="description" widget="markdown_editor"  options="{'height': 'auto','theme': 'dark', 'previewStyle':'vertical', }"/>
```

> `options` 参数说明:

| 选项|  类型 |说明 |
|----------|-----:|-----:|
|height|字符串 |高度 例如 `300px` 或者 `auto`|
|theme|字符串 |主题 `dark` 或者为 空 |
|previewStyle| 字符串|预览样式，可选有： 选项卡 `tab`, 垂直 `vertical`|
|userPlugin| 布尔值|使用组件，默认为`false`|


> 组件列表说明：

| 名称|  说明 |链接 |
|----------|-----:|-----:|
|chart|图表插件,`测试无法正常使用`| <a href="https://nhn.github.io/tui.editor/latest/tutorial-example07-editor-with-chart-plugin" target="_blank">打开链接</a>|
|code-syntax-highlight|代码语法突出显示插件,`可以正常使用`| <a href="https://nhn.github.io/tui.editor/latest/tutorial-example08-editor-with-code-syntax-highlight-plugin" target="_blank">打开链接</a>|
|colorSyntax|颜色语法插件,`测试无法正常使用`| <a href="https://nhn.github.io/tui.editor/latest/tutorial-example09-editor-with-color-syntax-plugin" target="_blank">打开链接</a>|
|tableMergedCell|表格合并单元格插件,`测试无法正常使用`| <a href="https://nhn.github.io/tui.editor/latest/tutorial-example10-editor-with-table-merged-cell-plugin" target="_blank">打开链接</a>|
|uml|UML 插件,`测试无法正常使用`| <a href="https://nhn.github.io/tui.editor/latest/tutorial-example11-editor-with-uml-plugin" target="_blank">打开链接</a>|


## 扫码
1. 支持条码及二维码
2. 支持同时扫码多个条码及二维码
3. 调用 `企业微信扫一扫` 仅支持单个条码及二维码

### `ScanCodeChar`
```xml
<field name="barcode" widget="ScanCodeChar" options="{'need_confirm': true, 'autoplay':true}" />
```

### `ScanCodeText`
```xml
<field name="barcode" widget="ScanCodeText" options="{'need_confirm': true, 'autoplay':true}" />
```

### `ScanCodeURL`
```xml
<field name="barcode" widget="ScanCodeURL" options="{'need_confirm': true, 'autoplay':true}" />
```

## 密码显示 `display_password`
```xml
<field name="contacts_secret" widget="DisplayPasswordChar" require_encryption="True" />
```

## 微软Office文件在线预览
```xml
<field name="word_file_path" widget="office_viewer" module_name="universities_management" storage_path="word" height="500" accept="application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"/>
```
#### 微软Office文件在线预览使用说明
1. `module_name` 文件需要保存的程序模块名称，`storage_path` 文件需要保存的目录，定义好这2个参数后，文件将保存到 `{module_name}\static\{storage_path}\{日期}`
2. `accept`:允许上传的文件格式，accept的接受的微软office文档 Mime 类型列表：

| 类型/子类型 | 扩展名 |  说明 |
|----------|:-------------|------:|
|application/msword	|doc | MS Word Document |
|application/vnd.openxmlformats-officedocument.wordprocessingml.document |docx | MS Word Document |
|application/msword	|dot | MS Word Template |
|application/vnd.ms-excel|	xla| |
|application/vnd.ms-excel|	xlc| MS Excel Chart|
|application/vnd.ms-excel|	xlm| MS Excel Macro|
|application/vnd.ms-excel|	xls| MS Excel Spreadsheet|
|application/vnd.openxmlformats-officedocument.spreadsheetml.sheet|	xlsx| MS Excel Spreadsheet|
|application/vnd.ms-excel|	xlt| |
|application/vnd.ms-excel|	xlw| MS Excel Workspace|
|application/vnd.ms-outlook|	msg| |
|application/vnd.ms-pkicertstore|	sst| |
|application/vnd.ms-pkiseccat|	cat| |
|application/vnd.ms-pkistl|	stl| |
|application/vnd.ms-powerpoint|	pot| MS PowerPoint Template|
|application/vnd.ms-powerpoint|	pps| MS PowerPoint Slideshow|
|application/vnd.ms-powerpoint|	ppt| MS PowerPoint Presentation|
|application/vnd.openxmlformats-officedocument.presentationml.presentation|	pptx| MS PowerPoint Presentation|
|application/vnd.ms-project|	mpp| MS Project Project|
|application/vnd.ms-works|	wcm| |
|application/vnd.ms-works|	wdb| MS Works Database|
|application/vnd.ms-works|	wks| |
|application/vnd.ms-works|	wps| Works Text Document|


## 一对多配置 one2many_config
```xml
<field name="contacts_app_config_ids" widget="one2many_config" format="value" type="ttype" help="description" class="w-100 pl-3" t-translation="off">
    <tree create="0" edit="true" delete="0" editable="bottom" sample="1">
        <field name="name" readonly="1"/>
        <field name="key" readonly="1"/>
        <field name="value" need_format="true" force_save="1" required="1"/>
        <field name="description" invisible="1"/>
    </tree>
</field>
```