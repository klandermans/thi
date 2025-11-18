const { Client, LocalAuth } = require('whatsapp-web.js');



const qrcode = require('qrcode-terminal');

// Maak een nieuwe client aan
const client = new Client({
    authStrategy: new LocalAuth(), // Bewaart de sessie lokaal
});

// QR-code genereren en tonen in de terminal
client.on('qr', (qr) => {
    console.log('Scan de QR-code met WhatsApp om in te loggen:');
    qrcode.generate(qr, { small: true });
});

// Client succesvol ingelogd
client.on('ready', () => {
    console.log('WhatsApp Bot is klaar!');
});

// Bericht ontvangen en automatisch antwoorden
client.on('message', async (message) => {
    console.log(`Bericht ontvangen van ${message.from}: ${message.body}`);
    
    if (message.body.toLowerCase() === 'hallo') {
        await message.reply('Hallo! Hoe kan ik je helpen?');
    } else if (message.body.toLowerCase() === 'hoe gaat het?') {
        await message.reply('Met mij gaat het goed! En met jou?');
    } else {
        await message.reply('Sorry, ik begrijp je niet. Probeer "hallo" of "hoe gaat het?"');
    }
});

// Start de client
client.initialize();

