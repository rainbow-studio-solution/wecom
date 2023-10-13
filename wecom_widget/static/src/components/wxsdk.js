/** @odoo-module **/

const {
    Component,
    useState,
    useRef,
    onWillStart,
    onMounted,
    onWillUnmount
} = owl;


export class WecomSdk extends Component {
    setup() {
        super.setup();

        onWillStart(async () => {
            await loadBundle({
                jsLibs: [
                    
                ],
            });
        });
    }
}