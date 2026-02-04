use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;
use tauri::{Emitter, Manager};
use std::sync::Mutex;

struct SidecarState {
    port: Mutex<Option<String>>,
}

#[tauri::command]
fn get_sidecar_port(state: tauri::State<'_, SidecarState>) -> Option<String> {
    state.port.lock().unwrap().clone()
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(SidecarState {
            port: Mutex::new(None),
        })
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![greet, get_sidecar_port])
        .setup(|app| {
            let handle = app.handle().clone();
            let sidecar = app.shell().sidecar("sidecar").unwrap();
            let (mut rx, _child) = sidecar.spawn().expect("Failed to spawn sidecar");

            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            let out = String::from_utf8_lossy(&line);
                            println!("[PY]: {}", out);
                            
                            // Parse dynamic port
                            if out.contains("PORT:") {
                                if let Some(port_str) = out.split("PORT:").last() {
                                    let port = port_str.trim().to_string();
                                    println!("Found sidecar port: {}", port);
                                    
                                    // Update state
                                    let state = handle.state::<SidecarState>();
                                    *state.port.lock().unwrap() = Some(port.clone());
                                    
                                    handle.emit("sidecar-ready", port).unwrap();
                                }
                            }
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("[PY ERR]: {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Terminated(status) => {
                            println!("Sidecar terminated with status: {:?}", status);
                            handle.emit("sidecar-error", format!("Sidecar process terminated with code {:?}", status.code)).unwrap();
                        }
                        _ => {}
                    }
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
