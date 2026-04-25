const vscode = require("vscode");

function activate(context) {

    let disposable = vscode.commands.registerCommand(
        "docstring.generate",
        async function () {

            const editor = vscode.window.activeTextEditor;

            if (!editor) {
                vscode.window.showErrorMessage("Abra um arquivo primeiro");
                return;
            }

            const code = editor.document.getText();

            vscode.window.showInformationMessage("Gerando docstrings...");

            try {
                const res = await fetch("http://localhost:8000/docstring", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ code })
                });

                const data = await res.json();

                if (data.error) {
                    vscode.window.showErrorMessage(data.error);
                    return;
                }

                const edit = new vscode.WorkspaceEdit();

                const fullRange = new vscode.Range(
                    editor.document.positionAt(0),
                    editor.document.positionAt(code.length)
                );

                edit.replace(editor.document.uri, fullRange, data.result);

                await vscode.workspace.applyEdit(edit);

                vscode.window.showInformationMessage("Docstrings geradas!");

            } catch (err) {
                vscode.window.showErrorMessage(err.message);
            }
        }
    );

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = { activate, deactivate };
