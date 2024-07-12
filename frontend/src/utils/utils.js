import toast from 'react-hot-toast'

const customToast = (message, icon, style) => {
	toast(message, {
		icon: icon,
		style: style,
	})
}

export { customToast }
