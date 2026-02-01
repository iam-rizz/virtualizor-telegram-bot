from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from src.routers.base import (
    auth_check,
    get_nav_buttons,
    BTN_BACK,
    FOOTER,
)

router = Router()

TITLE_VM = "*Virtual Machines*\n━━━━━━━━━━━━━━━━━━━━━\n\n"

OS_MAP = {
    "almalinux-8-x86_64": "AlmaLinux 8",
    "almalinux-8.8-x86_64": "AlmaLinux 8.8",
    "almalinux-9-x86_64": "AlmaLinux 9",
    "centos-7-x86_64": "CentOS 7",
    "debian-10.0-x86_64": "Debian 10",
    "debian-11.0-x86_64": "Debian 11",
    "debian-12-x86_64": "Debian 12",
    "debian-13-x86_64": "Debian 13",
    "ubuntu-20.04-x86_64": "Ubuntu 20.04",
    "ubuntu-22.04-x86_64": "Ubuntu 22.04",
    "ubuntu-24.04-x86_64": "Ubuntu 24.04",
}


def get_os_name(os_raw: str) -> str:
    if not os_raw:
        return "N/A"
    return OS_MAP.get(os_raw, os_raw)


def escape_md(text: str) -> str:
    chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in chars:
        text = str(text).replace(char, f"\\{char}")
    return text


def format_size(gb) -> str:
    try:
        gb = float(gb)
    except (ValueError, TypeError):
        return "0 GB"
    if gb >= 1024:
        return f"{gb / 1024:.1f} TB"
    return f"{gb:.1f} GB"


def format_ram(mb) -> str:
    try:
        mb = float(mb)
    except (ValueError, TypeError):
        return "0 GB"
    return f"{mb / 1024:.2f} GB"


def format_bandwidth(gb) -> str:
    try:
        gb = float(gb)
    except (ValueError, TypeError):
        return "0 GB"
    if gb >= 1024:
        return f"{gb / 1024:.1f} TB"
    return f"{gb:.1f} GB"


def progress_bar(used, total, length: int = 10) -> str:
    try:
        used = float(used)
        total = float(total)
    except (ValueError, TypeError):
        return "░" * length
    if total <= 0:
        return "░" * length
    percent = min(used / total, 1.0)
    filled = int(length * percent)
    return "█" * filled + "░" * (length - filled)


@router.callback_query(F.data == "menu_vms")
async def show_vms_menu(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = (
            TITLE_VM + "_No API configured\\._\n\n"
            "You need to add an API connection first to view your virtual machines\\.\n"
            "Go to API Management to add your Virtualizor credentials\\." + FOOTER
        )
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=BTN_BACK, callback_data="menu_main"))
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        return

    if len(apis) == 1:
        await _show_vm_list(callback, apis[0])
        return

    text = (
        TITLE_VM + "You have multiple API servers configured\\.\n"
        "Select which Virtualizor panel to view VMs from\\.\n\n"
        "_\\* indicates default API_" + FOOTER
    )

    builder = InlineKeyboardBuilder()
    for api in apis:
        default = " *" if api["is_default"] else ""
        builder.button(
            text=f"{api['name']}{default}", callback_data=f"vmapi_{api['name']}"
        )
    builder.adjust(2)

    builder.row(InlineKeyboardButton(text=BTN_BACK, callback_data="menu_main"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("vmapi_"))
async def vm_select_api(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    api_name = callback.data.replace("vmapi_", "")
    api_config = await db.get_api(api_name)

    if not api_config:
        text = (
            TITLE_VM + "_API not found\\._\n\n"
            "The selected API configuration could not be found\\." + FOOTER
        )
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_vms", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        return

    await _show_vm_list(callback, api_config)


async def _show_vm_list(callback: CallbackQuery, api_config: dict):
    api_name = api_config["name"]
    escaped_api_name = escape_md(api_name)

    text = TITLE_VM + f"*API:* `{escaped_api_name}`\n\n_Loading VMs\\.\\.\\._"
    await callback.message.edit_text(text)

    try:
        api = VirtualizorAPI.from_db_config(api_config)
        vms = api.list_vms()

        if not vms:
            text = (
                TITLE_VM + f"*API:* `{escaped_api_name}`\n\n"
                "_No VMs found\\._\n\n"
                "This Virtualizor panel has no virtual machines configured\\." + FOOTER
            )
            builder = InlineKeyboardBuilder()
            for btn in get_nav_buttons("menu_vms", True):
                builder.add(btn)
            builder.adjust(2)
            await callback.message.edit_text(text, reply_markup=builder.as_markup())
            return

        text = (
            f"*Virtual Machines* \\({len(vms)}\\)\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*API:* `{escaped_api_name}`\n\n"
            "Select a VM to view details\\.\n"
            "● Running  ○ Stopped  ◌ Suspended\n\n"
        )

        builder = InlineKeyboardBuilder()
        for vm in vms:
            if vm["status"] == "running":
                status_icon = "●"
            elif vm["status"] == "suspended":
                status_icon = "◌"
            else:
                status_icon = "○"
            hostname = escape_md(vm["hostname"])
            ip = escape_md(vm["ipv4"] or "No IP")
            vcpu = vm.get("vcpu", 0)
            ram = format_ram(vm.get("ram", 0))
            disk = format_size(vm.get("disk", 0))
            sys_os = escape_md(get_os_name(vm.get("os", "")))

            text += (
                f"{status_icon} *{hostname}*\n"
                f"    `{ip}`\n"
                f"    {sys_os}\n"
                f"    {vcpu} vCPU \\| {escape_md(ram)} RAM \\| {escape_md(disk)} Storage\n\n"
            )

            btn_name = (
                vm["hostname"][:15] + ".."
                if len(vm["hostname"]) > 15
                else vm["hostname"]
            )
            builder.button(
                text=f"{status_icon} {btn_name}",
                callback_data=f"vm_{api_config['name']}_{vm['vpsid']}",
            )

        text += FOOTER
        builder.adjust(2)

        builder.row(
            InlineKeyboardButton(
                text="Refresh", callback_data=f"vmapi_{api_config['name']}"
            )
        )

        nav_builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_vms", True):
            nav_builder.add(btn)
        nav_builder.adjust(2)
        builder.attach(nav_builder)

        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    except APIConnectionError as e:
        text = (
            f"*Connection Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Unable to connect to the Virtualizor panel\\.\n\n"
            f"`{escape_md(str(e))}`" + FOOTER
        )
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_vms", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    except AuthenticationError:
        text = (
            "*Authentication Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_Invalid API credentials\\._\n\n"
            "Please check your API Key and Password in API Management\\." + FOOTER
        )
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_vms", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    except APIError as e:
        text = (
            f"*API Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "An error occurred while fetching VMs\\.\n\n"
            f"`{escape_md(str(e))}`" + FOOTER
        )
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_vms", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "vm_list")
async def vm_list(callback: CallbackQuery):
    await show_vms_menu(callback)


@router.callback_query(F.data.startswith("vm_"))
async def vm_detail(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        return

    api_name = parts[1]
    vpsid = parts[2]
    escaped_api_name = escape_md(api_name)

    api_config = await db.get_api(api_name)
    if not api_config:
        return

    text = "*VM Details*\n━━━━━━━━━━━━━━━━━━━━━\n\n_Loading\\.\\.\\._"
    await callback.message.edit_text(text)

    try:
        api = VirtualizorAPI.from_db_config(api_config)
        vms = api.list_vms()

        vm = None
        for v in vms:
            if v["vpsid"] == vpsid:
                vm = v
                break

        if not vm:
            text = (
                "*VM Details*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "_VM not found\\._\n\n"
                "The virtual machine could not be found\\. "
                "It may have been deleted or the VPS ID is invalid\\." + FOOTER
            )
            builder = InlineKeyboardBuilder()
            for btn in get_nav_buttons(f"vmapi_{api_name}", True):
                builder.add(btn)
            builder.adjust(2)
            await callback.message.edit_text(text, reply_markup=builder.as_markup())
            return

        stats = api.get_vm_stats(vpsid)

        if vm["status"] == "running":
            status_text = "Running"
            status_icon = "●"
        elif vm["status"] == "suspended":
            status_text = "Suspended"
            status_icon = "◌"
        else:
            status_text = "Stopped"
            status_icon = "○"

        hostname = escape_md(vm["hostname"])
        ipv4 = escape_md(vm["ipv4"]) if vm["ipv4"] else "N/A"
        ipv6 = escape_md(vm["ipv6"]) if vm.get("ipv6") else "N/A"
        escaped_vpsid = escape_md(vpsid)

        vcpu = vm.get("vcpu", 0)
        ram_total = stats.get("ram_total", 0) or vm.get("ram", 0)
        ram_used = stats.get("ram_used", 0)
        disk_total = stats.get("disk_total", 0) or vm.get("disk", 0)
        disk_used = stats.get("disk_used", 0)
        bandwidth_total = stats.get("bandwidth_total", 0) or vm.get("bandwidth", 0)
        bandwidth_used = stats.get("bandwidth_used", 0) or vm.get("used_bandwidth", 0)
        nw_rules = stats.get("nw_rules", 0)
        os_name = escape_md(get_os_name(vm.get("os", "")))
        virt = escape_md(vm.get("virt", "")) if vm.get("virt") else "N/A"

        bw_bar = progress_bar(bandwidth_used, bandwidth_total)
        ram_bar = progress_bar(ram_used, ram_total)
        disk_bar = progress_bar(disk_used, disk_total)

        ram_used_str = escape_md(format_ram(ram_used)) if ram_used else "N/A"
        ram_total_str = escape_md(format_ram(ram_total))
        disk_used_str = escape_md(format_size(disk_used)) if disk_used else "N/A"
        disk_total_str = escape_md(format_size(disk_total))
        bw_used_str = (
            escape_md(format_bandwidth(bandwidth_used)) if bandwidth_used else "N/A"
        )
        bw_total_str = escape_md(format_bandwidth(bandwidth_total))

        text = (
            f"*{hostname}*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Status:* {status_icon} {status_text}\n"
            f"*VPS ID:* `{escaped_vpsid}`\n"
            f"*API:* `{escaped_api_name}`\n\n"
            "*Network*\n"
            "━━━━━━━\n"
            f"*IPv4:* `{ipv4}`\n"
            f"*IPv6:* `{ipv6}`\n"
            f"*Bandwidth:* `{bw_bar}`\n"
            f"{bw_used_str} / {bw_total_str}\n"
            f"*Port Forwarding:* {nw_rules} rule\\(s\\)\n\n"
            "*Resources*\n"
            "━━━━━━━━\n"
            f"*vCPU:* {vcpu} Core\\(s\\)\n\n"
            f"*RAM:* `{ram_bar}`\n"
            f"{ram_used_str} / {ram_total_str}\n\n"
            f"*Disk:* `{disk_bar}`\n"
            f"{disk_used_str} / {disk_total_str}\n\n"
            "*System*\n"
            "━━━━━━\n"
            f"*OS:* {os_name}\n"
            f"*Virtualization:* {virt}" + FOOTER
        )

        builder = InlineKeyboardBuilder()

        if vm["status"] == "running":
            builder.row(
                InlineKeyboardButton(
                    text="Restart", callback_data=f"vmact_{api_name}_{vpsid}_restart"
                ),
                InlineKeyboardButton(
                    text="Stop", callback_data=f"vmact_{api_name}_{vpsid}_stop"
                ),
            )
            builder.row(
                InlineKeyboardButton(
                    text="Power Off",
                    callback_data=f"vmact_{api_name}_{vpsid}_poweroff",
                )
            )
        elif vm["status"] == "stopped":
            builder.row(
                InlineKeyboardButton(
                    text="Start", callback_data=f"vmact_{api_name}_{vpsid}_start"
                )
            )

        builder.row(
            InlineKeyboardButton(text="Refresh", callback_data=f"vm_{api_name}_{vpsid}")
        )

        nav_builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons(f"vmapi_{api_name}", True):
            nav_builder.add(btn)
        nav_builder.adjust(2)
        builder.attach(nav_builder)

        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    except (APIConnectionError, AuthenticationError, APIError) as e:
        text = (
            f"*Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "An error occurred while fetching VM details\\.\n\n"
            f"`{escape_md(str(e))}`" + FOOTER
        )
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons(f"vmapi_{api_name}", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("vmact_"))
async def vm_action_handler(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        return

    api_name = parts[1]
    vpsid = parts[2]
    action = parts[3]

    api_config = await db.get_api(api_name)
    if not api_config:
        return

    action_names = {
        "start": "Starting",
        "stop": "Stopping",
        "restart": "Restarting",
        "poweroff": "Powering off",
    }
    action_name = action_names.get(action, action)

    text = (
        f"*VM Action*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"_{action_name} VM\\.\\.\\._\n\n"
        "Please wait\\.\\.\\."
    )
    await callback.message.edit_text(text)

    try:
        api = VirtualizorAPI.from_db_config(api_config)
        api.vm_action(vpsid, action)

        action_past = {
            "start": "started",
            "stop": "stopped",
            "restart": "restarted",
            "poweroff": "powered off",
        }
        action_done = action_past.get(action, action)

        text = (
            f"*VM Action*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"VM successfully {action_done}\\.\n\n"
            f"*VPS ID:* `{escape_md(vpsid)}`\n"
            f"*Action:* {escape_md(action.title())}\n\n"
            "_Refreshing VM details\\.\\.\\._"
        )
        await callback.message.edit_text(text)

        import asyncio

        await asyncio.sleep(2)

        await vm_detail(callback)

    except APIError as e:
        text = (
            f"*VM Action Failed*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Failed to {action} VM\\.\n\n"
            f"*Error:* `{escape_md(str(e))}`\n\n"
            "Please try again or check the Virtualizor panel\\." + FOOTER
        )
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="Retry", callback_data=f"vmact_{api_name}_{vpsid}_{action}"
            ),
            InlineKeyboardButton(text="< Back", callback_data=f"vm_{api_name}_{vpsid}"),
        )
        nav_builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons(f"vmapi_{api_name}", True):
            nav_builder.add(btn)
        nav_builder.adjust(2)
        builder.attach(nav_builder)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

    except (APIConnectionError, AuthenticationError) as e:
        text = (
            f"*Connection Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Unable to connect to Virtualizor panel\\.\n\n"
            f"*Error:* `{escape_md(str(e))}`" + FOOTER
        )
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="< Back", callback_data=f"vm_{api_name}_{vpsid}")
        )
        nav_builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons(f"vmapi_{api_name}", True):
            nav_builder.add(btn)
        nav_builder.adjust(2)
        builder.attach(nav_builder)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
