// @ts-nocheck
const macroDataEl = document.getElementById("macro-data");
const parsed = JSON.parse(macroDataEl.textContent);

const macroStyles = parsed.macro_styles;
const macroImages = parsed.macro_images;
const imageFiles = parsed.image_files;
const dynamicLabels = parsed.dynamic_macros;

const MAX_DYNAMIC = 10;
const added = new Set();
let removeMode = false;
let renameOldProfile = null;
let macroRemovedDuringTimeout = false;

let removeTimeout = null;
let timerInterval = null;
let timeRemaining = 0;

let suppressMenuSound = false;

const glowMap = {
  red: "rgba(255, 80, 80, 0.75)", // warmer coral-like glow
  blue: "rgba(80, 180, 255, 0.75)", // soft cyan to contrast dark blue
  green: "rgba(120, 255, 160, 0.45)", // minty green for a lively glow
  yellow: "rgba(255, 220, 100, 0.6)", // golden glow to offset bright yellow
};

function vibrateHaptic() {
  if (typeof Android !== "undefined" && Android.vibrate) {
    Android.vibrate(30, 255);
  }
}

function updateServer(input) {
  const user = input.value || input.dataset?.user;
  const color = input.dataset?.color || "white";

  localStorage.setItem("selectedUser", user);

  const selected = document.querySelector(".user-selected");
  if (selected) {
    selected.style.color = color;
    selected.dataset.user = user;
  }

  const loginSound = document.getElementById("loginSound");
  if (loginSound) loginSound.play().catch(() => {});
  console.log("Switched to user:", user);
}

function toggleUserDropdown() {
  const container = document.querySelector(".user-dropdown");
  const list = document.getElementById("userDropdownList");
  const isNowOpen = !list.classList.contains("show");

  list.classList.toggle("show", isNowOpen);
  container.classList.toggle("open", isNowOpen);

  if (!suppressMenuSound) {
    const sound = document.getElementById("macroMenuSound");
    sound?.play().catch(() => {});
  }
}

function selectUser(div, silent = false) {
  const user = div.dataset.user;
  const color = div.dataset.color;

  document
    .querySelectorAll(".user-item")
    .forEach((el) => el.classList.remove("selected-user"));
  div.classList.add("selected-user");

  const selected = document.querySelector(".user-selected");
  selected.textContent = div.textContent;
  selected.style.color = color;
  selected.dataset.user = user;

  localStorage.setItem("selectedUser", user);

  updateServer(div); // ← triggers login sound and user change

  loadProfileList(user);

  // Always close the dropdown
  const list = document.getElementById("userDropdownList");
  list.classList.remove("show");
  document.querySelector(".user-dropdown")?.classList.remove("open");

  // Suppress menu sound only if not silent
  if (!silent) {
    suppressMenuSound = true;
    setTimeout(() => {
      suppressMenuSound = false;
    }, 100);
  }
}

function loadProfileList(user) {
  fetch(`/list_profiles?user=${user}`)
    .then((res) => res.json())
    .then((data) => {
      populateCustomProfileList(data.profiles);
      window.currentProfileList = data.profiles;
    })
    .catch((err) => console.error("Loadout list fetch failed", err));
}

function loadProfileFromServer(selectEl) {
  const profileName = selectEl.value;
  const user = document.querySelector(".user-selected").dataset.user;
  const encodedProfile = encodeURIComponent(profileName.toLowerCase());
  fetch(`/get_profile?user=${user}&profile=${encodedProfile}`)
    .then((res) => res.json())
    .then((data) => {
      const macroGrid = document.getElementById("macroGrid");
      macroGrid.innerHTML = "";
      added.clear();

      if (!data.macros || !Array.isArray(data.macros)) {
        console.warn("No macros loaded from server response", data);
        alert("Failed to load macros for selected profile.");
        return;
      }

      data.macros.forEach(selectMacro);
    })
    .catch((err) => console.error("Loadout load failed", err));
}

function openDeleteModal() {
  const selectedEl = document.querySelector(".selected-profile");
  if (!selectedEl) return alert("Select a profile to delete.");

  const profile = selectedEl.textContent.trim();
  document.getElementById(
    "deleteMessage"
  ).textContent = `Delete loadout '${profile}'?`;
  document.getElementById("deleteModal").classList.add("visible");
  document
    .getElementById("pipSound")
    ?.play()
    .catch(() => {});
}

function closeDeleteModal() {
  document.getElementById("deleteModal").classList.remove("visible"); // hide
}

function confirmDeleteProfile() {
  const selectedEl = document.querySelector(".selected-profile");
  if (!selectedEl) return alert("Select a profile to delete.");

  const profileName = selectedEl.textContent.trim();
  const user = document.querySelector(".user-selected").dataset.user;
  fetch("/delete_profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, profile: profileName }),
  })
    .then((res) => res.json())
    .then(() => {
      alert("Loadout deleted.");
      closeDeleteModal();

      const selected = document.querySelector(".profile-selected");
      if (selected) selected.textContent = "Select Loadout";

      document
        .querySelectorAll(".profile-item")
        .forEach((el) => el.classList.remove("selected-profile"));

      loadProfileList(user);
    })
    .catch((err) => {
      console.error("Failed to delete loadout", err);
      alert("Error deleting loadout.");
      closeDeleteModal();
    });
}

function openSaveModal() {
  document.getElementById("saveInput").value = "";
  document.getElementById("overwriteWarning").style.display = "none";
  document.getElementById("saveModal").classList.add("visible");
  document.getElementById("saveInput").focus();
  document
    .getElementById("pipSound")
    ?.play()
    .catch(() => {});
}

function closeSaveModal() {
  document.getElementById("saveModal").classList.remove("visible"); // hide
}

function openRenameModal() {
  const selectedEl = document.querySelector(".selected-profile");
  if (!selectedEl) return alert("Select a profile to rename.");
  const profile = selectedEl.textContent;

  renameOldProfile = profile;
  document.getElementById("renameInput").value = "";
  document.getElementById("renameModal").classList.add("visible");
  document.getElementById("renameInput").focus();

  document
    .getElementById("pipSound")
    ?.play()
    .catch(() => {});
}

function closeRenameModal() {
  document.getElementById("renameModal").classList.remove("visible"); // hide
}

function confirmSaveProfile() {
  const profileName = document
    .getElementById("saveInput")
    .value.trim()
    .toLowerCase(); // force lowercase
  const user = document.querySelector(".user-selected").dataset.user;
  if (!profileName) return alert("Enter a loadout name");

  const macroButtons = document.querySelectorAll(
    "#macroGrid .macro-button button"
  );
  const macros = Array.from(macroButtons)
    .map((btn) => {
      // Prefer data-macro attribute
      const macroKey = btn.dataset.macro;
      if (macroKey) return macroKey;

      // Fallback: Try to reverse map from label or alt
      const label =
        btn.innerText.trim() || (btn.querySelector("img")?.alt?.trim() ?? "");
      return Object.keys(dynamicLabels).find(
        (key) => dynamicLabels[key] === label
      );
    })
    .filter(Boolean);

  const baseMacros = ["Reinforce", "Resupply"];
  const finalMacros = baseMacros.concat(
    macros.filter((m) => !baseMacros.includes(m))
  );

  fetch(`/save_profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, profile: profileName, macros: finalMacros }),
  })
    .then((res) => res.json())
    .then(() => {
      alert("Loadout saved.");
      loadProfileList(user);
      // Refresh preview icons after saving
      setTimeout(() => {
        const selected = document.querySelector(".profile-selected")?.textContent.trim();
        if (selected) populateCustomProfileList(window.currentProfileList || []);
      }, 300);
      closeSaveModal();

      setTimeout(() => {
        const selected = document.querySelector(".profile-selected");
        selected.textContent = profileName;

        document
          .querySelectorAll(".profile-item")
          .forEach((el) => el.classList.remove("selected-profile"));

        const match = Array.from(
          document.querySelectorAll(".profile-item")
        ).find((el) => el.textContent.trim() === profileName);

        if (match) match.classList.add("selected-profile");
      }, 200);
    })
    .catch((err) => {
      console.error("Save error", err);
      alert("Failed to save loadout");
    });
}

document.getElementById("saveInput").addEventListener("input", function () {
  const name = this.value.trim().toLowerCase(); // normalize input
  const existing = window.currentProfileList?.map((p) => p.toLowerCase()) || [];
  const warning = document.getElementById("overwriteWarning");
  warning.style.display = existing.includes(name) ? "block" : "none";
});

function confirmRenameProfile() {
  const newName = document.getElementById("renameInput").value.trim();
  const user = document.querySelector(".user-selected").dataset.user;
  if (!renameOldProfile || !newName) return alert("Missing loadout name");
  if (window.currentProfileList?.includes(newName)) {
    if (!confirm(`Loadout '${newName}' exists. Overwrite it?`)) return;
  }
  fetch(`/rename_profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user,
      old_profile: renameOldProfile,
      new_profile: newName,
    }),
  })
    .then((res) => res.json())
    .then(() => {
      alert("Renamed.");
      loadProfileList(user);
      closeRenameModal();

      setTimeout(() => {
        const selected = document.querySelector(".profile-selected");
        selected.textContent = newName;

        document
          .querySelectorAll(".profile-item")
          .forEach((el) => el.classList.remove("selected-profile"));

        const match = Array.from(
          document.querySelectorAll(".profile-item")
        ).find((el) => el.textContent.trim() === newName);

        if (match) match.classList.add("selected-profile");
      }, 200);
    })
    .catch((err) => {
      console.error("Rename error", err);
      alert("Rename failed");
    });
}

function openQuickUpdateModal() {
  const selectedEl = document.querySelector(".selected-profile");
  if (!selectedEl) return alert("Select a profile to update.");

  const profile = selectedEl.textContent.trim();
  document.getElementById(
    "quickUpdateMessage"
  ).textContent = `Are you sure you want to overwrite the loadout '${profile}'?`;
  document.getElementById("quickUpdateModal").classList.add("visible");
  document
    .getElementById("pipSound")
    ?.play()
    .catch(() => {});
}

function closeQuickUpdateModal() {
  document.getElementById("quickUpdateModal").classList.remove("visible");
}

function confirmQuickUpdate() {
  const selectedEl = document.querySelector(".selected-profile");
  if (!selectedEl) return alert("Select a profile to update.");

  const profileName = selectedEl.textContent.trim();
  const user = document.querySelector(".user-selected").dataset.user;

  const macroButtons = document.querySelectorAll(
    "#macroGrid .macro-button button"
  );
  const macros = Array.from(macroButtons)
    .map((btn) => {
      const macroKey = btn.dataset.macro;
      if (macroKey) return macroKey;
      const label =
        btn.innerText.trim() || (btn.querySelector("img")?.alt?.trim() ?? "");
      return Object.keys(dynamicLabels).find(
        (key) => dynamicLabels[key] === label
      );
    })
    .filter(Boolean);

  const baseMacros = ["Reinforce", "Resupply"];
  const finalMacros = baseMacros.concat(
    macros.filter((m) => !baseMacros.includes(m))
  );

  fetch(`/save_profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user,
      profile: profileName.toLowerCase(),
      macros: finalMacros,
    }),
  })
    .then((res) => res.json())
    .then(() => {
      alert(`Loadout '${profileName}' updated.`);
      loadProfileList(user);
      // Refresh preview icons after saving
      setTimeout(() => {
        const selected = document.querySelector(".profile-selected")?.textContent.trim();
        if (selected) populateCustomProfileList(window.currentProfileList || []);
      }, 300);
      closeQuickUpdateModal();
      const sound = document.getElementById("confirmSound");
      if (sound) sound.play().catch(() => {});
    })
    .catch((err) => {
      console.error("Quick update failed", err);
      alert("Failed to update loadout.");
      closeQuickUpdateModal();
    });
}

function toggleRemoveMode() {
  const btn = document.getElementById("removeBtn");
  const status = document.getElementById("removeStatus");
  const timer = document.getElementById("removeTimer");

  vibrateHaptic();
  document
    .getElementById("removeToggleSound")
    ?.play()
    .catch(() => {});

  if (removeMode) {
    // Turn OFF manually
    clearTimeout(removeTimeout);
    clearInterval(timerInterval);
    removeMode = false;
    status.innerText = "OFF";
    timer.innerText = "";
    btn.style.backgroundColor = "";
    return;
  }

  // Turn ON
  removeMode = true;
  let timeRemaining = 5;
  status.innerText = "ON";
  timer.innerText = `(${timeRemaining})`;
  btn.style.backgroundColor = "darkred";

  timerInterval = setInterval(() => {
    timeRemaining--;
    timer.innerText = `(${timeRemaining})`;

    if (timeRemaining <= 0) {
      clearInterval(timerInterval);
    }
  }, 1000);

  removeTimeout = setTimeout(() => {
    removeMode = false;
    status.innerText = "OFF";
    timer.innerText = "";
    btn.style.backgroundColor = "";
    vibrateHaptic();
  }, 5000);
}

function triggerMacro(name) {
  const user = document.querySelector(".user-selected").dataset.user;
  fetch(`/trigger/${name}?user=${user}`)
    .then((res) => res.json())
    .then(() => console.log(`Triggered: ${name}`))
    .catch((err) => console.error("Trigger failed", err));
  const sound = document.getElementById("macroSound");
  if (sound) sound.play().catch(() => {});
  vibrateHaptic();
}

const LOCKED_MACROS = ["Reinforce", "Resupply"];

function selectMacro(label) {
  const name = label;
  const macroGrid = document.getElementById("macroGrid");
  if (!label || added.has(label) || macroGrid.children.length >= MAX_DYNAMIC)
    return;
  const labelText = dynamicLabels[name] || name;
  const image = macroImages[name];
  const hasImage = image && imageFiles.includes(image);
  const isLocked = LOCKED_MACROS.includes(name);

  const wrapper = document.createElement("div");
  wrapper.className = "macro-button";
  updateGridOffset();

  const sound = document.getElementById("macroAddSound");
  if (sound) sound.play().catch(() => {});

  const baseColor = macroStyles[name].border;
  const glowColor = glowMap[baseColor] || baseColor;

  if (macroStyles[name]?.border) {
    wrapper.style.border = `2px solid ${baseColor}`;
    wrapper.style.boxShadow = `0 0 12px 3px ${glowColor}`; // outer glow
  }

  const button = document.createElement("button");
  button.dataset.macro = name;
  button.onclick = () => {
    if (removeMode) {
      if (isLocked) {
        alert(`'${name}' cannot be removed.`);
        return;
      }
      macroGrid.removeChild(wrapper);
      added.delete(name);
      macroRemovedDuringTimeout = true;
      // Restart the timer
      clearTimeout(removeTimeout);
      clearInterval(timerInterval);

      let timeRemaining = 5;
      document.getElementById("removeTimer").innerText = `(${timeRemaining})`;

      timerInterval = setInterval(() => {
        timeRemaining--;
        document.getElementById("removeTimer").innerText = `(${timeRemaining})`;

        if (timeRemaining <= 0) {
          clearInterval(timerInterval);
        }
      }, 1000);

      removeTimeout = setTimeout(() => {
        removeMode = false;
        document.getElementById("removeStatus").innerText = "OFF";
        document.getElementById("removeTimer").innerText = "";
        document.getElementById("removeBtn").style.backgroundColor = "";
        vibrateHaptic();
      }, 5000);
      const sound = document.getElementById("macroRemoveSound");
      if (sound) sound.play().catch(() => {});
      updateGridOffset();
      if (macroGrid.children.length < MAX_DYNAMIC) {
        document.querySelector(".dropdown-toggle").classList.remove("disabled");
        document.querySelector(".dropdown-selected").textContent = "Stratagems";
      }
    } else {
      triggerMacro(name);
    }
  };

  if (hasImage) {
    const img = document.createElement("img");
    img.src = `/static/images/${image}`;
    img.alt = labelText;
    button.appendChild(img);
  } else {
    button.innerText = labelText;
  }

  wrapper.appendChild(button);
  macroGrid.appendChild(wrapper);
  added.add(name);

  const dropdown = document.getElementById("macroDropdown");
  dropdown.classList.remove("show");

  if (macroGrid.children.length >= MAX_DYNAMIC) {
    document.querySelector(".dropdown-toggle").classList.add("disabled");
    document.querySelector(".dropdown-selected").textContent = "Max Reached";
  }
}

function toggleDropdown() {
  const row = document.querySelector(".dropdown-toggle");
  const list = document.getElementById("macroDropdown");

  const isDisabled = row.classList.contains("disabled");
  if (isDisabled) {
    document
      .getElementById("macroMaxSound")
      ?.play()
      .catch(() => {});
    return;
  }

  const isOpen = list.classList.toggle("show");
  row.classList.toggle("open", isOpen); // Add/remove open class on stratagem-row

  const sound = document.getElementById("macroMenuSound");
  if (!suppressMenuSound && sound) sound.play().catch(() => {});
}

function toggleProfileDropdown() {
  const dropdown = document.querySelector(".profile-dropdown");
  const list = document.getElementById("profileDropdownList");

  const isOpen = list.classList.toggle("show");
  dropdown.classList.toggle("open", isOpen);

  const sound = document.getElementById("macroMenuSound");
  if (!suppressMenuSound && sound) sound.play().catch(() => {});
}

function populateCustomProfileList(profiles) {
  const list = document.getElementById("profileDropdownList");
  list.innerHTML = ""; // Clear existing items

  const currentSelected = document
    .querySelector(".profile-selected")
    ?.textContent.trim();

  profiles.forEach((profile) => {
    const div = document.createElement("div");
    div.className = "profile-item";

    const nameSpan = document.createElement("span");
    nameSpan.className = "profile-name";
    nameSpan.textContent = profile;
    div.appendChild(nameSpan);

    if (profile === currentSelected) {
      div.classList.add("selected-profile");
    }

    const previewContainer = document.createElement("div");
    previewContainer.className = "profile-preview";

    const user = document.querySelector(".user-selected")?.dataset.user;
    const encodedProfile = encodeURIComponent(profile.toLowerCase());

    fetch(`/get_profile?user=${user}&profile=${encodedProfile}`)
      .then((res) => res.json())
      .then((data) => {
        if (data?.macros?.length) {
          data.macros
            .filter((name) => {
              const clean = name.trim().toLowerCase();
              return clean !== "resupply" && clean !== "reinforce";
            })
            .slice(0, 10)
            .forEach((macroName) => {
              const image = macroImages[macroName];
              if (!image || !imageFiles.includes(image)) return;

              const img = document.createElement("img");
              img.src = `/static/images/${image}`;
              img.alt = macroName;
              img.className = "macro-preview-icon";
              previewContainer.appendChild(img);
            });
        }
      })
      .catch((err) => console.error("Preview fetch error", err));

    div.appendChild(previewContainer);
    list.appendChild(div);
  });
}

function updateGridOffset() {
  requestAnimationFrame(() => {
    const grid = document.getElementById("macroGrid");
    const container = document.querySelector(".macro-grid-container");
    const children = Array.from(grid.children);

    if (children.length === 0) {
      container.classList.remove("align-center");
      return;
    }

    const firstTop = children[0].offsetTop;
    const hasMultipleRows = children.some(
      (child) => child.offsetTop !== firstTop
    );

    if (hasMultipleRows) {
      container.classList.add("align-center"); // Center when multiple rows
    } else {
      container.classList.remove("align-center"); // Top when only 1 row
    }
  });
}

window.onload = () => {
  const macroGrid = document.getElementById("macroGrid");
  const storedUser = localStorage.getItem("selectedUser");

  if (storedUser) {
    const matchingUser = Array.from(
      document.querySelectorAll(".user-item")
    ).find((el) => el.dataset.user === storedUser);
    if (matchingUser) selectUser(matchingUser, true); // ← pass true to avoid opening
  }

  if (macroGrid.children.length >= MAX_DYNAMIC) {
    document.querySelector(".dropdown-toggle").classList.add("disabled");
  }

  // 🔥 Apply glow effects to statically-rendered macros
  const macroButtons = document.querySelectorAll("#macroGrid .macro-button");

  macroButtons.forEach((wrapper) => {
    const img = wrapper.querySelector("img");
    if (!img) return;

    const label = img.alt; // or use dataset if available
    const style = macroStyles[label];
    if (!style || !style.border) return;

    const baseColor = style.border;
    const glowColor = glowMap[baseColor] || baseColor;

    wrapper.style.border = `2px solid ${baseColor}`;
    wrapper.style.boxShadow = `0 0 12px 3px ${glowColor}`;
  });
};

window.onclick = (e) => {
  const previouslySuppressed = suppressMenuSound;
  suppressMenuSound = false;
  const dropdown = document.getElementById("macroDropdown");
  if (!e.target.closest(".dropdown-container"))
    dropdown.classList.remove("show");
};

document
  .getElementById("profileDropdownList")
  ?.addEventListener("click", (e) => {
    const item = e.target.closest(".profile-item");
    if (!item) return;

    document
      .querySelectorAll(".profile-item")
      .forEach((el) => el.classList.remove("selected-profile"));
    item.classList.add("selected-profile");

    const selected = document.querySelector(".profile-selected");
    selected.textContent = item.textContent;

    const list = document.getElementById("profileDropdownList");
    const container = document.querySelector(".profile-dropdown");

    const wasOpen = list.classList.contains("show");
    list.classList.remove("show");
    container.classList.remove("open");

    // Prevent menu sound on profile selection per issue
    if (wasOpen && !suppressMenuSound && e.isTrusted) {
      if (!e.target.closest(".profile-item")) {
        document
          .getElementById("macroMenuSound")
          ?.play()
          .catch(() => {});
      }
    }

    loadProfileFromServer({ value: item.textContent });
  });

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeRenameModal();
});
document.addEventListener("click", (e) => {
  // Explicitly track suppression state at the top of the block
  const wasSuppressed = suppressMenuSound;
  suppressMenuSound = false;

  // Play sound for cancel/confirm buttons
  if (e.target.closest("button")) {
    const btn = e.target.closest("button");
    const text = btn.innerText.toLowerCase();

    if (text.includes("cancel")) {
      document
        .getElementById("cancelSound")
        ?.play()
        .catch(() => {});
    } else if (text.includes("confirm")) {
      document
        .getElementById("confirmSound")
        ?.play()
        .catch(() => {});
    }
  }

  // Close macro dropdown
  if (!e.target.closest(".dropdown-toggle")) {
    const list = document.getElementById("macroDropdown");
    const wasOpen = list?.classList.contains("show");
    list?.classList.remove("show");
    document.querySelector(".dropdown-toggle")?.classList.remove("open");
    if (wasOpen && !wasSuppressed) {
      document
        .getElementById("macroMenuSound")
        ?.play()
        .catch(() => {});
    }
  }

  // Close user dropdown
  if (!e.target.closest(".user-dropdown")) {
    const list = document.getElementById("userDropdownList");
    const wasOpen = list?.classList.contains("show");
    list?.classList.remove("show");
    document.querySelector(".user-dropdown")?.classList.remove("open");
    if (wasOpen && !wasSuppressed) {
      document
        .getElementById("macroMenuSound")
        ?.play()
        .catch(() => {});
    }
  }

  // Close profile dropdown
  if (!e.target.closest(".profile-dropdown")) {
    const list = document.getElementById("profileDropdownList");
    const wasOpen = list?.classList.contains("show");
    list?.classList.remove("show");
    document.querySelector(".profile-dropdown")?.classList.remove("open");
    if (wasOpen && !wasSuppressed) {
      document
        .getElementById("macroMenuSound")
        ?.play()
        .catch(() => {});
    }
  }

  // suppressMenuSound is already reset at the top
});
document.querySelectorAll(".user-item").forEach((item) => {
  item.onclick = (e) => {
    e.stopPropagation(); // Prevents click from bubbling to document-level handler
    selectUser(item);
  };
});
