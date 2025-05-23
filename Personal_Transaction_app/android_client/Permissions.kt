fun Activity.requestSmsPermission() {
    ActivityCompat.requestPermissions(
        this,
        arrayOf(Manifest.permission.RECEIVE_SMS, Manifest.permission.READ_SMS),
        1001
    )
}
