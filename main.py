from flask import Flask, render_template, request, render_template_string, redirect
from urllib.parse import quote

telefone = "5531998229269"  
app = Flask(__name__)

xbr = 0
xb = 0
b = 0 
lista_pedidos = []

valorxbr = 15
valorxb = 18
valorb = 12

@app.route("/", methods=["GET"])
def inicio():
    global xbr, xb, b, lista_pedidos
    xbr, xb, b = 0, 0, 0
    lista_pedidos = []
    return render_template("index.html", lista="")

@app.route("/adicionar", methods=["POST"])
def adicionar():
    global xbr, xb, b
    
    produto = request.form.get("produto")
    
    if produto == "xburguer":
        lista_pedidos.append(1)
        xbr += 1
    elif produto == "xbacon":
        lista_pedidos.append(2)
        xb += 1
    elif produto == "batata":
        lista_pedidos.append(3)
        b += 1

    lista = f"{xbr} X-burguer    |    {xb} X-bacon    |    {b} Batata"
    
    return f"""
        <div id="Pedido" style="display: flex; flex-direction: column; align-items: center; align-content: center;">
            <h2>Seu Pedido Atual:</h2>
            <p id="l">{lista}</p>
            <a href="/formulario" style="margin-top: 10px; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Ir para o Formulário</a>
        </div>
        """


@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    entrega_ativa = False
    taxa = 0
    nome_usuario = ""  
    
    if request.method == "POST":
        tipo = request.form.get("tipo_recepcao")
        nome_usuario = request.form.get("nome", "")
        
        if tipo == "entrega":
            entrega_ativa = True
            taxa = 5
        else:
            entrega_ativa = False
            taxa = 0

    qtd_xbr = lista_pedidos.count(1)
    qtd_xb = lista_pedidos.count(2)
    qtd_b = lista_pedidos.count(3)

    subtotal = (qtd_xbr * valorxbr) + (qtd_xb * valorxb) + (qtd_b * valorb)
    total = subtotal + taxa


    bloco_conteudo = """
        <div id="resumo-pedido">
            <div id="conteudo-formulario">
                
                <div class="grupo-campo">
                    <label for="nome">Qual o seu nome completo? *</label>
                    <textarea name="nome" id="nome" placeholder="Digite seu nome aqui..." required>{{ nome }}</textarea>
                </div>

                <div class="grupo-campo">
                    <label>Como você prefere receber seu pedido? *</label>
                    <div id="buttons">
                        <div id="entrega">
                            <button 
                                type="button" 
                                class="tipo_recepcao" 
                                hx-post="/formulario"
                                hx-include="#nome"
                                hx-vals='{"tipo_recepcao": "entrega"}'
                                hx-target="#resumo-pedido"
                                hx-swap="innerHTML"
                            >Entrega em casa</button>
                        </div>

                        <div id="local">
                            <button 
                                type="button" 
                                class="tipo_recepcao" 
                                hx-post="/formulario"
                                hx-include="#nome"
                                hx-vals='{"tipo_recepcao": "retirada"}'
                                hx-target="#resumo-pedido"
                                hx-swap="innerHTML"
                            >Retirar no balcão</button>
                        </div>
                    </div>
                </div>

                {% if entrega %}
                <input type="hidden" name="tipo_recepcao" value="entrega">
                <div id="entregar">
                    <div class="p1">
                        <div id="ran">
                            <label for="rua">Rua ou Avenida *</label>
                            <textarea placeholder="Ex: Av. Afonso Pena" name="rua" id="rua" required></textarea>
                        </div>
                        <div>
                            <label for="numero">Número *</label>
                            <textarea placeholder="Ex: 123" name="numero" id="numero" required></textarea>
                        </div>
                    </div>
                    <div>
                        <label for="bairro">Bairro *</label>
                        <textarea placeholder="Ex: Centro" name="bairro" id="bairro" required></textarea>

                        <label for="ref">Ponto de Referência ou Complemento (Opcional)</label>
                        <textarea placeholder="Ex: Apto 202, próximo à padaria" name="ref" id="ref"></textarea>
                    </div>
                </div>
                {% else %}
                <input type="hidden" name="tipo_recepcao" value="retirada">
                {% endif %}
            </div>

            <div id="pix" class="bloco-pix">
                <h3>Chave Pix para pagamento (CPF)</h3>
                <p class="chave-pix">000.000.000-00</p>
            </div>

            <div class="resumo-valores">
                <div class="linha-valor"><span>Subtotal:</span> <strong>R$ {{ subtotal }}</strong></div>
                <hr>
                <div class="linha-valor"><span>Taxa de entrega:</span> <strong>R$ {{ taxa }}</strong></div>
                <hr>
                <div class="linha-valor total"><span>Total a pagar:</span> <strong>R$ {{ total }}</strong></div>
            </div>

            <button type="submit" id="enviar-pedido" class="botao-enviar">Enviar Pedido no WhatsApp</button>
        </div>
    """

    if request.headers.get("HX-Request"):
        return render_template_string(bloco_conteudo, entrega=entrega_ativa, taxa=taxa, subtotal=subtotal, total=total, nome=nome_usuario)
    
    return render_template("formulario.html", entrega=entrega_ativa, subtotal=subtotal, taxa=taxa, total=total, nome=nome_usuario)


@app.route("/finalizar", methods=["POST"])
def finalizar():
    nome = request.form.get("nome", "")
    tipo_recepcao = request.form.get("tipo_recepcao")
    
    qtd_xbr = lista_pedidos.count(1)
    qtd_xb = lista_pedidos.count(2)
    qtd_b = lista_pedidos.count(3)

    texto_pedido = f"Olá! Me chamo {nome} e gostaria de fazer o seguinte pedido:\n\n"
    if qtd_xbr > 0:
        texto_pedido += f"- {qtd_xbr}x X-Burguer\n"
    if qtd_xb > 0:
        texto_pedido += f"- {qtd_xb}x X-Bacon\n"
    if qtd_b > 0:
        texto_pedido += f"- {qtd_b}x Batata\n"

    if tipo_recepcao == "entrega":
        rua = request.form.get("rua", "")
        numero = request.form.get("numero", "")
        bairro = request.form.get("bairro", "")
        ref = request.form.get("ref", "")
        
        texto_pedido += f"\nModo: Entrega em domicílio"
        texto_pedido += f"\nEndereço: Rua {rua}, nº {numero} - Bairro {bairro}"
        if ref:
            texto_pedido += f"\nReferência: {ref}"
    else:
        texto_pedido += f"\nModo: Retirada no balcão"

    subtotal = (qtd_xbr * valorxbr) + (qtd_xb * valorxb) + (qtd_b * valorb)
    taxa = 5 if tipo_recepcao == "entrega" else 0
    total = subtotal + taxa
    
    texto_pedido += f"\n\nTotal a pagar: R$ {total}"

    mensagem_url = quote(texto_pedido)
    link_whatsapp = f"https://api.whatsapp.com/send?phone={telefone}&text={mensagem_url}"

    return redirect(link_whatsapp)

if __name__ == "__main__":
    app.run(debug=True)