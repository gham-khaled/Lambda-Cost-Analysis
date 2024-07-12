import { PrimeReactProvider } from 'primereact/api'

import AppRouter from './routes/AppRouter'

export default function App() {
	return (
		<PrimeReactProvider>
			<AppRouter />
		</PrimeReactProvider>
	)
}
