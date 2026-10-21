<div align="center">

# YOSHI Control Studio

**Macros, perfis personalizados e configurações de entrada em uma única interface.**

[![Versão oficial](https://img.shields.io/github/v/release/saviodebug/yoshi-updates?label=vers%C3%A3o&color=9250d2)](https://github.com/saviodebug/yoshi-updates/releases/latest)
![Plataforma](https://img.shields.io/badge/plataforma-Windows%20x64-9250d2)

### [↓ Baixar a versão oficial](https://github.com/saviodebug/yoshi-updates/releases/latest)

</div>

## Sobre o YOSHI

O YOSHI reúne ferramentas de personalização de funções, perfis e controles de entrada. A interface mantém suas configurações organizadas para alternar entre diferentes formas de uso.

## Funcionalidades

A versão publicada **1.5.2** inclui:

- Configuração de macros de corrida, Auto Aim, Litefoot e No Recoil.
- Mira visual configurável.
- Criação, gerenciamento, importação e exportação de perfis.
- Configuração de atalhos de teclado e botões do mouse.
- Editor de scripts Lua, com validação, importação e exportação.
- Atualizações pelo aplicativo com verificação do manifesto e do arquivo baixado.

**Em desenvolvimento:** central visual de macros, mapeamento visual de dispositivos, diagnóstico de periféricos, monitoramento de eventos/polling e informações de bateria para dispositivos compatíveis. Esses recursos não devem ser presumidos disponíveis na versão 1.5.2.

## Download

Baixe o arquivo `.exe` na [release oficial mais recente](https://github.com/saviodebug/yoshi-updates/releases/latest). Consulte as notas dessa versão antes de atualizar.

## Instalação

1. Salve o executável em uma pasta no seu computador Windows.
2. Execute o arquivo e confirme a solicitação de permissão do Windows.
3. Informe sua licença válida quando solicitado.

A distribuição atual é um executável direto, sem assistente de instalação. Não é necessário instalar nada. A pasta usada deve permitir a gravação dos arquivos exportados pelo aplicativo.

## Atualizações automáticas

As atualizações oficiais são distribuídas pelas Releases deste repositório. O aplicativo consulta o manifesto da versão, apresenta a atualização disponível e verifica a assinatura, o tamanho e o hash do download antes da instalação.

Versões anteriores à migração para o GitHub podem precisar de uma atualização pelo canal anterior ou do download manual da versão atual para passar a utilizar o novo canal.

## Segurança

O atualizador verifica a autenticidade do manifesto com assinatura Ed25519 e a integridade do executável com SHA-256. O executável publicado é compilado; isso não significa criptografia integral nem impede engenharia reversa.

A versão 1.5.2 não possui assinatura Authenticode. A verificação automatizada deste repositório confere os arquivos publicados, sem executar o aplicativo. Novas versões estão sujeitas às verificações e aos bloqueios do processo privado de produção.

## Compatibilidade

- Aplicativo para Windows de 64 bits, validado em Windows 11 x64.
- Licença válida e conexão para os serviços de ativação e atualização.
- As funções de macro atuais são voltadas ao MTA e podem depender da janela em primeiro plano e das configurações de entrada.

A telemetria em desenvolvimento depende das interfaces e dos protocolos de cada periférico. A identificação de uma marca ou modelo não garante leitura de bateria ou frequência física de polling.

## Versões

Consulte o [histórico de releases e suas notas](https://github.com/saviodebug/yoshi-updates/releases).

## Contato e suporte

Este repositório reúne os [downloads e comunicados de versão oficiais](https://github.com/saviodebug/yoshi-updates/releases). Não há outro canal de suporte divulgado aqui. Nunca publique sua chave de licença ou dados pessoais em locais públicos.

## Avisos

Utilize macros respeitando as regras dos aplicativos, jogos e serviços envolvidos. A disponibilidade de uma função não representa autorização ou aprovação de terceiros.
