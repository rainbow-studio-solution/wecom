odoo.define('web_widget_markdown_tests', function (require) {
    "use strict";
    var FormView = require('web.FormView');
    var testUtils = require('web.test_utils');
    var core = require('web.core');
    var _t = core._t;

    QUnit.module('Markdown Widget Tests', {
            beforeEach: function () {
                this.data = {
                    blog: {
                        fields: {
                            name: {
                                string: "Name",
                                type: "char"
                            },
                            content: {
                                string: "Content",
                                type: "text"
                            },
                        },
                        records: [{
                                id: 1,
                                name: "Blog Post 1",
                                content: "# Hello world",
                            },
                            {
                                id: 2,
                                name: "Blog Post 2",
                                content: "## Second title",
                            },
                        ]
                    }
                };
            }
        },
        function () {
            QUnit.test('web_widget_markdown readonly test 1', async function (assert) {
                assert.expect(2);
                var form = await testUtils.createView({
                    View: FormView,
                    model: 'blog',
                    data: this.data,
                    arch: '<form string="Blog">' +
                        '<group>' +
                        '<field name="name"/>' +
                        '<field name="content" widget="markdown"/>' +
                        '</group>' +
                        '</form>',
                    res_id: 1,
                });
                assert.strictEqual(
                    form.$('.o_field_markdown').find("h1").length,
                    1,
                    "h1 should be present"
                )
                assert.strictEqual(
                    form.$('.o_field_markdown h1').text(),
                    "Hello world",
                    "<h1> should contain 'Hello world'"
                )
                form.destroy();
            });
            QUnit.test('web_widget_markdown readonly test 2', async function (assert) {
                assert.expect(2);
                var form = await testUtils.createView({
                    View: FormView,
                    model: 'blog',
                    data: this.data,
                    arch: '<form string="Blog">' +
                        '<group>' +
                        '<field name="name"/>' +
                        '<field name="content" widget="markdown"/>' +
                        '</group>' +
                        '</form>',
                    res_id: 2,
                });
                assert.strictEqual(
                    form.$('.o_field_markdown').find("h2").length,
                    1,
                    "h2 should be present"
                )
                assert.strictEqual(
                    form.$('.o_field_markdown h2').text(),
                    "Second title",
                    "<h2> should contain 'Second title'"
                )
                form.destroy();
            });
            QUnit.test('web_widget_markdown SimpleMDE is present', async function (assert) {
                assert.expect(1);
                var form = await testUtils.createView({
                    View: FormView,
                    model: 'blog',
                    data: this.data,
                    arch: '<form string="Blog">' +
                        '<group>' +
                        '<field name="name"/>' +
                        '<field name="content" widget="markdown"/>' +
                        '</group>' +
                        '</form>',
                    res_id: 1,
                });
                await testUtils.form.clickEdit(form);
                assert.strictEqual(
                    form.$('.o_field_markdown').find("div.CodeMirror").length,
                    1,
                    "CodeMirror div should be present"
                )
                form.destroy();
            });
            QUnit.test('web_widget_markdown edit SimpleMDE', async function (assert) {
                assert.expect(4);
                var form = await testUtils.createView({
                    View: FormView,
                    model: 'blog',
                    data: this.data,
                    arch: '<form string="Blog">' +
                        '<group>' +
                        '<field name="name"/>' +
                        '<field name="content" widget="markdown"/>' +
                        '</group>' +
                        '</form>',
                    res_id: 1,
                });
                await testUtils.form.clickEdit(form);
                var markdownField = _.find(form.renderer.allFieldWidgets)[1];

                assert.strictEqual(
                    markdownField.simplemde.value(),
                    "# Hello world",
                    "Initial Value of SimpleMDE should be set"
                )

                markdownField.simplemde.value('**bold content**');
                assert.strictEqual(
                    markdownField._getValue(),
                    "**bold content**",
                    "If we change value in SimpleMDE, value of odoo widget should be updated"
                )

                await testUtils.form.clickSave(form);
                assert.strictEqual(
                    form.$('.o_field_markdown').find("strong").length,
                    1,
                    "After Save, b should be present"
                )
                assert.strictEqual(
                    form.$('.o_field_markdown strong').text(),
                    "bold content",
                    "After Save, <strong> should contain 'bold content'"
                )
                form.destroy();
            });

            QUnit.test('markdown widget field translatable', async function (assert) {
                assert.expect(12);

                this.data.blog.fields.content.translate = true;

                var multiLang = _t.database.multi_lang;
                _t.database.multi_lang = true;

                var form = await testUtils.createView({
                    View: FormView,
                    model: 'blog',
                    data: this.data,
                    arch: '<form string="Blog">' +
                        '<group>' +
                        '<field name="name"/>' +
                        '<field name="content" widget="markdown"/>' +
                        '</group>' +
                        '</form>',
                    res_id: 1,
                    session: {
                        user_context: {
                            lang: 'en_US'
                        },
                    },
                    mockRPC: function (route, args) {
                        if (route === "/web/dataset/call_button" && args.method === 'translate_fields') {
                            assert.deepEqual(args.args, ["blog", 1, "content"], 'should call "call_button" route');
                            return Promise.resolve({
                                domain: [],
                                context: {
                                    search_default_name: 'blog,content'
                                },
                            });
                        }
                        if (route === "/web/dataset/call_kw/res.lang/get_installed") {
                            return Promise.resolve([
                                ["en_US", "English"],
                                ["fr_BE", "French (Belgium)"]
                            ]);
                        }
                        if (args.method === "search_read" && args.model == "ir.translation") {
                            return Promise.resolve([{
                                    lang: 'en_US',
                                    src: '# Hello world',
                                    value: '# Hello world',
                                    id: 42
                                },
                                {
                                    lang: 'fr_BE',
                                    src: '# Hello world',
                                    value: '# Bonjour le monde',
                                    id: 43
                                }
                            ]);
                        }
                        if (args.method === "write" && args.model == "ir.translation") {
                            assert.deepEqual(args.args[1], {
                                    value: "# Hellow mister Johns"
                                },
                                "the new translation value should be written");
                            return Promise.resolve();
                        }
                        return this._super.apply(this, arguments);
                    },
                });
                await testUtils.form.clickEdit(form);
                var $translateButton = form.$('div.o_field_markdown + .o_field_translate');
                assert.strictEqual($translateButton.length, 1, "should have a translate button");
                assert.strictEqual($translateButton.text(), 'EN', 'the button should have as test the current language');
                await testUtils.dom.click($translateButton);
                await testUtils.nextTick();

                assert.containsOnce($(document), '.modal', 'a translate modal should be visible');
                assert.containsN($('.modal .o_translation_dialog'), '.translation', 2,
                    'two rows should be visible');

                var $dialogENSourceField = $('.modal .o_translation_dialog .translation:first() input');
                assert.strictEqual($dialogENSourceField.val(), '# Hello world',
                    'English translation should be filled');
                assert.strictEqual($('.modal .o_translation_dialog .translation:last() input').val(), '# Bonjour le monde',
                    'French translation should be filled');

                await testUtils.fields.editInput($dialogENSourceField, "# Hellow mister Johns");
                await testUtils.dom.click($('.modal button.btn-primary')); // save
                await testUtils.nextTick();

                var markdownField = _.find(form.renderer.allFieldWidgets)[1];
                assert.strictEqual(markdownField._getValue(), "# Hellow mister Johns",
                    "the new translation was not transfered to modified record");

                markdownField.simplemde.value('**This is new English content**');
                await testUtils.nextTick();
                // Need to wait nextTick for data to be in markdownField.value and passed 
                // to the next dialog open
                await testUtils.dom.click($translateButton);
                await testUtils.nextTick();

                assert.strictEqual($('.modal .o_translation_dialog .translation:first() input').val(), '**This is new English content**',
                    'Modified value should be used instead of translation');
                assert.strictEqual($('.modal .o_translation_dialog .translation:last() input').val(), '# Bonjour le monde',
                    'French translation should be filled');

                form.destroy();

                _t.database.multi_lang = multiLang;
            });

            QUnit.test('web_widget_markdown passing property to SimpleMDE', async function (assert) {
                assert.expect(1);
                var form = await testUtils.createView({
                    View: FormView,
                    model: 'blog',
                    data: this.data,
                    arch: `<form string="Blog">
                        <group>
                            <field name="name"/>
                            <field name="content" widget="markdown" options="{'placeholder': 'Begin writing here...'}"/>
                        </group>
                    </form>`,
                    res_id: 1,
                });
                await testUtils.form.clickEdit(form);
                var markdownField = _.find(form.renderer.allFieldWidgets)[1];
                assert.strictEqual(
                    markdownField.simplemde.options.placeholder,
                    "Begin writing here...",
                    "SimpleMDE should have the correct placeholder"
                );

                await testUtils.form.clickSave(form);
                form.destroy();
            });
        }
    );
});