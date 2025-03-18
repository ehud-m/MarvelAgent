import { useState } from "react";
import {
    Input,
    Button,
    List,
    Typography,
    Spin,
    Layout,
    message as AntMessage, Modal,
} from "antd";

const { Header, Content, Footer } = Layout;
const { TextArea } = Input;

export default function ChatAntdUI() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [charCount, setCharCount] = useState("");
    const [canIngest, setCanIngest] = useState(false);
    const [graphCharacter, setGraphCharacter] = useState("");
    const [graphModalVisible, setGraphModalVisible] = useState(false);
    const [graphModalContent, setGraphModalContent] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/question", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage.content }),
            });

            const data = await res.json();
            const botMessage = { role: "assistant", content: data.message };
            setMessages((prev) => [...prev, botMessage]);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const buildDataset = async () => {
        try {
            await fetch("http://localhost:8000/data/build", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
            AntMessage.success("Dataset built successfully");
            setCanIngest(true);
        } catch (err) {
            AntMessage.error("Failed to build dataset");
        }
    };

    const getCharacterGraph = async () => {
        if (!graphCharacter.trim()) return;
        try {
            const res = await fetch(`http://localhost:8000/graph/${encodeURIComponent(graphCharacter)}`);
            const data = await res.json();
//             const resultMessage = `Graph neighbors for ${graphCharacter}:
// ` +
//                 data.map((item) => `- ${item.relation} → ${item.name} (${item.labels.join(", ")})`).join("\n");
            setGraphModalContent(data);
            setGraphModalVisible(true);
        } catch (err) {
            AntMessage.error("Failed to fetch graph data");
        }
    };

    const ingestDataset = async () => {
        if (!charCount || isNaN(Number(charCount))) return;
        try {
            await fetch(`http://localhost:8000/data/ingest`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ number_of_characters: charCount }),
            });
            AntMessage.success("Dataset ingested successfully");
        } catch (err) {
            AntMessage.error("Failed to ingest dataset");
        }
    };

    return (
        <Layout style={{ minHeight: "100vh" }}>
            <Header style={{ color: "white", fontWeight: "bold", fontSize: "1.25rem" }}>
                Marvel Knowledge Assistant
            </Header>
            <Content style={{ padding: "24px", maxWidth: 800, margin: "auto" }}>
                <List
                    bordered
                    dataSource={messages}
                    renderItem={(item) => (
                        <List.Item>
                            <div style={{ width: "100%" }}>
                                <Typography.Text strong>
                                    {item.role === "user" ? "OMGene User" : "OMGene Marvel Master"}:
                                </Typography.Text>
                                <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>{item.content}</div>
                            </div>
                        </List.Item>
                    )}
                    style={{ marginBottom: "16px", background: "white" }}
                />

                {loading && <Spin style={{ marginBottom: "1rem" }} />}

                <TextArea
                    rows={2}
                    placeholder="Ask something about Marvel..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    style={{ marginBottom: 8 }}
                />
                <Button type="primary" onClick={sendMessage} disabled={loading}>
                    Send
                </Button>

                <div style={{ marginTop: 32 }}>
                    <Typography.Title level={5}>Dataset Utilities</Typography.Title>
                    <Button onClick={buildDataset} style={{ marginRight: 12 }}>Build Dataset</Button>
                    <Input
                        type="number"
                        placeholder="Write # of characters to ingest"
                        value={charCount}
                        onChange={(e) => setCharCount(e.target.value)}
                        style={{ width: 300, marginRight: 8 }}
                        allowClear
                        disabled={!canIngest}
                    />
                    <Button
                        type="dashed"
                        onClick={ingestDataset}
                        disabled={!canIngest || !charCount || isNaN(Number(charCount))}
                    >
                        Ingest Dataset
                    </Button>
                    <Typography.Title level={5}>Graph Explorer</Typography.Title>
                    <Input
                        placeholder="Enter character name (e.g. Wolverine)"
                        value={graphCharacter}
                        onChange={(e) => setGraphCharacter(e.target.value)}
                        style={{ width: 300, marginRight: 8 }}
                        allowClear
                    />
                    <Button onClick={getCharacterGraph} type="default">
                        Get Character Graph
                    </Button>

                    <Modal
                        title={`Graph Neighbors for ${graphCharacter}`}
                        open={graphModalVisible}
                        onCancel={() => setGraphModalVisible(false)}
                        footer={null}
                    >
                        <pre>{graphModalContent}</pre>
                    </Modal>
                </div>
            </Content>
            <Footer style={{ textAlign: "center" }}>Powered by FastAPI & LangGraph</Footer>
        </Layout>
    );
}