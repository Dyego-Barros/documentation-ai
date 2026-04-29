const vscode = require("vscode");
const fs = require("fs");
const path = require("path");

function activate(context) {

    // =========================
    // 📌 DOCSTRING
    // =========================
    let docCommand = vscode.commands.registerCommand(
        "docstring.generate",
        async function () {

            const editor = vscode.window.activeTextEditor;

            if (!editor) {
                vscode.window.showErrorMessage("Abra um arquivo primeiro");
                return;
            }

            const code = editor.document.getText();
            const detectedLang = editor.document.languageId;

            const map = {
                python: "python",
                javascript: "javascript",
                typescript: "javascript",
                java: "java",
                csharp: "csharp",
                go: "go"
            };

            let language = map[detectedLang];

            if (!language) {
                language = await vscode.window.showQuickPick(
                    ["python", "javascript", "java", "csharp", "go"],
                    { placeHolder: "Escolha a linguagem" }
                );
            }

            if (!language) return;

            vscode.window.showInformationMessage(
                `Gerando docstrings para ${language}...`
            );

            try {
                const res = await fetch("http://localhost:8000/languages/docs", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ code, language })
                });

                if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);

                const data = await res.json();

                const edit = new vscode.WorkspaceEdit();
                const fullRange = new vscode.Range(
                    editor.document.positionAt(0),
                    editor.document.positionAt(code.length)
                );

                edit.replace(editor.document.uri, fullRange, data.result);
                await vscode.workspace.applyEdit(edit);

                vscode.window.showInformationMessage("Docstrings geradas!");

            } catch (err) {
                vscode.window.showErrorMessage("Erro: " + err.message);
            }
        }
    );

    // =========================
    // 🐳 DOCKER + COMPOSE
    // =========================
    let dockerCommand = vscode.commands.registerCommand(
        "dockerfile.generate",
        async function () {

            const workspaceFolders = vscode.workspace.workspaceFolders;

            if (!workspaceFolders) {
                vscode.window.showErrorMessage("Abra uma pasta/projeto");
                return;
            }

            const rootPath = workspaceFolders[0].uri.fsPath;

            const projects = findProjects(rootPath);

            if (projects.length === 0) {
                vscode.window.showErrorMessage("Nenhum projeto detectado");
                return;
            }

            vscode.window.showInformationMessage("Detectando serviços...");

            const services = [];

            for (const project of projects) {

                vscode.window.showInformationMessage(
                    `Gerando Dockerfile para ${project.name}...`
                );

                try {

                    const contextFiles = collectProjectFiles(project.path);

                    const res = await fetch("http://localhost:8000/generate/dockerfile", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            project_type: project.type,
                            files: contextFiles,
                            framework: contextFiles.framework
                        })
                    });

                    if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);

                    const data = await res.json();

                    // 🔥 NOVO MÉTODO (SEM WorkspaceEdit)
                    const filePath = path.join(project.path, "Dockerfile");
                    let content = null;

                    // caso 1: string direta
                    if (typeof data.result === "string") {
                        content = data.result;
                    }

                    // caso 2: padrão OpenAI-like
                    else if (data.result?.content) {
                        const texts = data.result.content
                            .map(c => c.text)
                            .filter(Boolean);

                        content = texts.join("\n");
                    }

                    // caso 3: fallback genérico
                    else if (typeof data === "string") {
                        content = data;
                    }

                    console.log("CONTENT FINAL:", content);

                    console.log("DOCKERFILE:", content);
                    console.log("SIZE:", content?.length);

                    if (!content || typeof content !== "string" || !content.trim()) {
                        vscode.window.showErrorMessage(
                            `Resposta vazia da IA para ${project.name}`
                        );
                        continue;
                    }

                    content = content
                        .replace(/```[\w]*\s*/g, "")
                        .replace(/```/g, "");

                    fs.writeFileSync(filePath, content, "utf-8");

                    services.push({
                        name: project.name === "root" ? "app" : project.name,
                        path: project.name === "root" ? "." : `./${project.name}`,
                        type: project.type
                    });

                } catch (err) {
                    vscode.window.showErrorMessage(
                        `Erro em ${project.name}: ` + err.message
                    );
                }
            }

            // =========================
            // 🐳 DOCKER-COMPOSE
            // =========================
            const generateCompose = await vscode.window.showQuickPick(
                ["Sim", "Não"],
                { placeHolder: "Deseja gerar docker-compose.yml?" }
            );

            if (generateCompose !== "Sim") return;

            try {

                const res = await fetch("http://localhost:8000/generate/compose", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ services })
                });

                if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);

                const data = await res.json();

                const composeFilePath = path.join(rootPath, "docker-compose.yml");
                //let content = data.result;
                let content = null;

                    // caso 1: string direta
                    if (typeof data.result === "string") {
                        content = data.result;
                    }

                    // caso 2: padrão OpenAI-like
                    else if (data.result?.content) {
                        const texts = data.result.content
                            .map(c => c.text)
                            .filter(Boolean);

                        content = texts.join("\n");
                    }

                    // caso 3: fallback genérico
                    else if (typeof data === "string") {
                        content = data;
                    }


                console.log("COMPOSE:", content);

                if (!content || typeof content !== "string" || !content.trim()) {
                    vscode.window.showErrorMessage("Resposta vazia para docker-compose");
                    return;
                }

                content = content
                    .replace(/```[\w]*\s*/g, "")
                    .replace(/```/g, "");

                fs.writeFileSync(composeFilePath, content, "utf-8");

                vscode.window.showInformationMessage(
                    "docker-compose.yml criado 🚀"
                );

            } catch (err) {
                vscode.window.showErrorMessage("Erro ao gerar compose: " + err.message);
            }
        }
    );

    context.subscriptions.push(docCommand);
    context.subscriptions.push(dockerCommand);
}

// =========================
// 🔍 DETECTAR PROJETOS
// =========================
function findProjects(rootPath) {
    const projects = [];

    if (isProject(rootPath)) {
        projects.push({
            name: "root",
            path: rootPath,
            type: detectProjectType(rootPath)
        });
    }

    const dirs = fs.readdirSync(rootPath, { withFileTypes: true });

    for (const dir of dirs) {
        if (!dir.isDirectory()) continue;

        const fullPath = path.join(rootPath, dir.name);

        if (isProject(fullPath)) {
            projects.push({
                name: dir.name,
                path: fullPath,
                type: detectProjectType(fullPath)
            });
        }
    }

    return projects;
}

// =========================
// 🔍 VALIDAR PROJETO
// =========================
function isProject(projectPath) {
    try {
        return (
            fs.existsSync(path.join(projectPath, "package.json")) ||
            fs.existsSync(path.join(projectPath, "requirements.txt")) ||
            fs.existsSync(path.join(projectPath, "pyproject.toml")) ||
            fs.existsSync(path.join(projectPath, "go.mod")) ||
            fs.existsSync(path.join(projectPath, "pom.xml")) ||
            fs.readdirSync(projectPath).some(f => f.endsWith(".csproj"))
        );
    } catch {
        return false;
    }
}

// =========================
// 🔍 DETECTAR TIPO
// =========================
function detectProjectType(projectPath) {

    if (fs.existsSync(path.join(projectPath, "package.json"))) return "node";
    if (fs.existsSync(path.join(projectPath, "requirements.txt"))) return "python";
    if (fs.existsSync(path.join(projectPath, "pyproject.toml"))) return "python";
    if (fs.existsSync(path.join(projectPath, "go.mod"))) return "go";
    if (fs.existsSync(path.join(projectPath, "pom.xml"))) return "java";

    const files = fs.readdirSync(projectPath);
    if (files.find(f => f.endsWith(".csproj"))) return "csharp";

    return "unknown";
}

// =========================
// 📂 COLETAR ARQUIVOS
// =========================
function collectProjectFiles(projectPath) {

    function read(file) {
        try {
            return fs.readFileSync(path.join(projectPath, file), "utf-8");
        } catch {
            return null;
        }
    }

    let csprojContent = null;
    try {
        const files = fs.readdirSync(projectPath);
        const csprojFile = files.find(f => f.endsWith(".csproj"));
        if (csprojFile) csprojContent = read(csprojFile);
    } catch {}

    const mainPy = read("main.py") || read("app.py");
    let framework = null;

    if (mainPy && mainPy.includes("FastAPI")) {
        framework = "fastapi";
    }

    return {
        packageJson: read("package.json"),
        requirements: read("requirements.txt"),
        pyproject: read("pyproject.toml"),
        goMod: read("go.mod"),
        pom: read("pom.xml"),
        csproj: csprojContent,
        framework
    };
}

function deactivate() {}

module.exports = { activate, deactivate };