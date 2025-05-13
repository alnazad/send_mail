<?php
// error_reporting(E_ALL);
// ini_set('display_errors', 1);
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'PHPMailer.php';
require 'SMTP.php';
require 'Exception.php';

$mail = new PHPMailer(true);
$mail->SMTPDebug = 2; // Show debug output
$mail->Debugoutput = 'html'; // Output format

try {
    // Server settings
    $mail->isSMTP();
    $mail->Host       = 'mail.devnazad.com';  // ✅ Use your actual SMTP server
    $mail->SMTPAuth   = true;
    $mail->Username   = 'nazad@devnazad.com';  // ✅ Your email address
    $mail->Password   = 'asdfghjk';             // ✅ Your email password
    $mail->SMTPSecure = 'tls';                             // Sometimes it's 'ssl'
    $mail->Port       = 587;                               // Or 465 for SSL

    // Sender and recipient
    // $mail->setFrom($_POST['email'], $_POST['name']);
    $mail->setFrom('nazad@devnazad.com');
    $mail->addAddress('abdullah@gmail.com');  // Your destination email

    // Content
    $mail->isHTML(false);
    $mail->Subject = $_POST['subject'];
    $mail->Body    = "Name: {$_POST['name']}\nEmail: {$_POST['email']}\n\nMessage:\n{$_POST['message']}";

    $mail->send();
    echo "メッセージが送信されました。ありがとうございます！";
} catch (Exception $e) {
    echo "メール送信エラー: {$mail->ErrorInfo}";
}
?>
