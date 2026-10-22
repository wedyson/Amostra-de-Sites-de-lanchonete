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

    lista = f"{xbr} X-burguer     |     {xb} X-bacon     |     {b} Batata"
    
    return f"""
        <div id="Pedido">
            <h2>Pedido:</h2>
            <p id="l">{lista}</p>
        </div>
        <div id="comprar">
            <button type="button" class="mercadoria" hx-post="/adicionar" hx-vals='{{"produto": "xburguer"}}' hx-target="#pedido" hx-swap="innerHTML">X-Burguer</button>
            <button type="button" class="mercadoria" hx-post="/adicionar" hx-vals='{{"produto": "xbacon"}}' hx-target="#pedido" hx-swap="innerHTML">X-Bacon</button>
            <button type="button" class="mercadoria" hx-post="/adicionar" hx-vals='{{"produto": "batata"}}' hx-target="#pedido" hx-swap="innerHTML">Batata</button>
            <a href="/formulario"><button type="button" id="finish">Finalizar Compra</button></a>
        </div>
        """

@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    entrega_ativa = False
    taxa = 0
    
    if request.method == "POST":
        tipo = request.form.get("tipo_recepcao")
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
                <p>NOME COMPLETO *</p>
                <textarea name="nome" id="nome" placeholder="Digite seu nome"></textarea>
                
                <p>COMO DESEJA RECEBER? *</p>
                <div id="buttons">
                    <div id="entrega">
                        <button 
                        type="button" 
                        class="tipo_recepcao" 
                        hx-post="/formulario"
                        hx-vals='{"tipo_recepcao": "entrega"}'
                        hx-target="#resumo-pedido"
                        hx-swap="innerHTML"
                        >Entrega</button>
                    </div>

                    <div id="local">
                        <button 
                        type="button" 
                        class="tipo_recepcao" 
                        hx-post="/formulario"
                        hx-vals='{"tipo_recepcao": "retirada"}'
                        hx-target="#resumo-pedido"
                        hx-swap="innerHTML"
                        >Retirar no Local</button>
                    </div>
                </div>

                {% if entrega %}
                <!-- Campo oculto para informar ao backend que é entrega -->
                <input type="hidden" name="tipo_recepcao" value="entrega">
                <div id="entregar">
                    <div class="p1">
                        <div id="ran">
                            <p>Rua/Avenida *</p>
                            <textarea placeholder="Ex: Av. Brasil" name="rua" id="rua"></textarea>
                        </div>
                        <div>
                            <p>Número *</p>
                            <textarea placeholder="123" name="numero" id="numero"></textarea>
                        </div>
                    </div>
                    <div>
                        <p>Bairro *</p>
                        <textarea placeholder="Ex: centro" name="bairro" id="bairro"></textarea>

                        <p>Complemento / Ref (opcional) *</p>
                        <textarea placeholder="Ex: Ap 102, perto da padaria" name="ref" id="ref"></textarea>
                    </div>
                </div>
                {% else %}
                <input type="hidden" name="tipo_recepcao" value="retirada">
                {% endif %}
            </div>

            <div id="pix">
                <h3>Chave Pix (CPF)</h3>
                <p>000.000.000-00</p>
            </div>
            <h2>Subtotal: R$ {{ subtotal }}</h2>
            <hr>
            <h2>Taxa de entrega: R$ {{ taxa }}</h2>
            <hr>
            <h2>Total: R$ {{ total }}</h2>
            
            <!-- Botão de enviar dentro do bloco dinâmico para submeter o formulário -->
            <button type="submit" id="enviar-pedido">Enviar Pedido no WhatsApp</button>
        </div>
    """

    if request.headers.get("HX-Request"):
        return render_template_string(bloco_conteudo, entrega=entrega_ativa, taxa=taxa, subtotal=subtotal, total=total)
    
    return render_template("formulario.html", entrega=entrega_ativa, subtotal=subtotal, taxa=taxa, total=total)


@app.route("/finalizar", methods=["POST"])
def finalizar():
    nome = request.form.get("nome", "")
    tipo_recepcao = request.form.get("tipo_recepcao")
    
    qtd_xbr = lista_pedidos.count(1)
    qtd_xb = lista_pedidos.count(2)
    qtd_b = lista_pedidos.count(3)

    texto_pedido = f"Olá! Meu nome é {nome}. Gostaria de pedir:\n"
    if qtd_xbr > 0:
        texto_pedido += f"- {qtd_xbr} X-Burguer\n"
    if qtd_xb > 0:
        texto_pedido += f"- {qtd_xb} X-Bacon\n"
    if qtd_b > 0:
        texto_pedido += f"- {qtd_b} Batata\n"

    if tipo_recepcao == "entrega":
        rua = request.form.get("rua", "")
        numero = request.form.get("numero", "")
        bairro = request.form.get("bairro", "")
        ref = request.form.get("ref", "")
        
        texto_pedido += f"\n*Modo:* Entrega\n*Endereço:* Rua {rua}, nº {numero}, Bairro {bairro}"
        if ref:
            texto_pedido += f" (Ref: {ref})"
    else:
        texto_pedido += f"\n*Modo:* Retirada no Local"

    subtotal = (qtd_xbr * valorxbr) + (qtd_xb * valorxb) + (qtd_b * valorb)
    taxa = 5 if tipo_recepcao == "entrega" else 0
    total = subtotal + taxa
    
    texto_pedido += f"\n*Total a pagar:* R$ {total}"

    mensagem_url = quote(texto_pedido)
    link_whatsapp = f"https://api.whatsapp.com/send?phone={telefone}&text={mensagem_url}"

    return redirect(link_whatsapp)

if __name__ == "__main__":
    app.run(debug=True)